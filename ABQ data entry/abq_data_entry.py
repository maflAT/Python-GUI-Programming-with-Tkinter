from abq_data_entry import Application


def main(args) -> None:
    app = Application()
    app.mainloop()


if __name__ == "__main__":
    import sys

    main_rv = main(sys.argv)
    sys.exit(main_rv)
