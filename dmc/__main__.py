from .app import DMCWebApp


def main():

    app = DMCWebApp()

    app.run(
        host="127.0.0.1",
        port=5000
    )


if __name__ == "__main__":
    main()