from website import create_app

application = create_app()

if __name__ == '__main__':
    # specify the port to bind to, and the IP to bind to 0.0.0.0 = bind to everything
    application.run(host='0.0.0.0', port=5000, debug=True)
