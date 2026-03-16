from update_answers import update_answers
from mailer_sender import mailer_sender


def main():
    update_answers()
    mailer_sender()


if __name__ == "__main__":
    main()
