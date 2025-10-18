from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enables Cross-Origin Resource Sharing for all routes

# 🗂️ In-memory list of blog posts
POSTS = [
    {"id": 1, "title": "First post", "content": "This is the first post."},
    {"id": 2, "title": "Second post", "content": "This is the second post."},
]

# 📋 GET /api/posts
# Returns a list of all posts. Supports optional sorting by title or content.
@app.route('/api/posts', methods=['GET'])
def get_posts():
    """
    Retrieve all posts, optionally sorted by title or content.

    Query Parameters:
        sort (str): Field to sort by ('title' or 'content').
        direction (str): Sort direction ('asc' or 'desc', default is 'asc').

    Returns:
        200 OK with sorted post list,
        400 Bad Request if parameters are invalid.
    """

    sort_field = request.args.get('sort')
    direction = request.args.get('direction', 'asc')

    valid_fields = ['title', 'content']
    valid_directions = ['asc', 'desc']

    if sort_field and sort_field not in valid_fields:
        return jsonify({"error": f"Invalid sort field: '{sort_field}'. Use 'title' or 'content'."}), 400
    if direction and direction not in valid_directions:
        return jsonify({"error": f"Invalid direction: '{direction}'. Use 'asc' or 'desc'."}), 400

    sorted_posts = POSTS.copy()
    if sort_field:
        reverse = direction == 'desc'
        sorted_posts.sort(key=lambda post: post[sort_field].lower(), reverse=reverse)

    return jsonify(sorted_posts), 200

# ➕ POST /api/posts
# Adds a new post. Requires 'title' and 'content' in the request body.
@app.route('/api/posts', methods=['POST'])
def add_post():
    """
    Add a new post from JSON input with title and content.

    Returns:
        201 Created with the new post,
        400 Bad Request if JSON body or required fields are missing.
    """

    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON body"}), 400

    missing_fields = []
    if "title" not in data or not data["title"]:
        missing_fields.append("title")
    if "content" not in data or not data["content"]:
        missing_fields.append("content")
    if missing_fields:
        return jsonify({"error": f"Missing field(s): {', '.join(missing_fields)}"}), 400

    new_id = max(post["id"] for post in POSTS) + 1 if POSTS else 1
    new_post = {
        "id": new_id,
        "title": data["title"],
        "content": data["content"]
    }
    POSTS.append(new_post)
    return jsonify(new_post), 201

# 🗑️ DELETE /api/posts/<id>
# Deletes a post by its ID. Returns 404 if the post is not found.
@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    """
    Delete a post by its ID from the in-memory POSTS list.

    Returns:
        200 OK if the post was deleted,
        404 Not Found if the post does not exist.
    """

    post = next((p for p in POSTS if p["id"] == post_id), None)
    if not post:
        return jsonify({"error": f"Post with id {post_id} not found."}), 404

    POSTS.remove(post)
    return jsonify({"message": f"Post with id {post_id} has been deleted successfully."}), 200

# ✏️ PUT /api/posts/<id>
# Updates an existing post by ID. Title and content are optional.
@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    data = request.get_json()
    post = next((p for p in POSTS if p["id"] == post_id), None)
    if not post:
        return jsonify({"error": f"Post with id {post_id} not found."}), 404

    post["title"] = data.get("title", post["title"])
    post["content"] = data.get("content", post["content"])
    return jsonify(post), 200

# 🔍 GET /api/posts/search
# Searches posts by title or content using query parameters.
@app.route('/api/posts/search', methods=['GET'])
def search_posts():
    title_query = request.args.get('title', '').lower()
    content_query = request.args.get('content', '').lower()

    results = [
        post for post in POSTS
        if title_query in post["title"].lower() or content_query in post["content"].lower()
    ]
    return jsonify(results), 200

# 🚀 Starts the Flask development server
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)

