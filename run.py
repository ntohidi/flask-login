from app import app  # create_app


def run_server():
    print("Start server...")
    # app = create_app()
    app.run(host='0.0.0.0', port=9090, debug=True)


if __name__ == "__main__":
    run_server()
