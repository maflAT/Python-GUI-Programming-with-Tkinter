from unittest import TestCase
from unittest.mock import Mock
import tkinter as tk
from .. import widgets as w


class TkTestCase(TestCase):
    """A test case designed for Tkinter widgets and views"""

    @classmethod
    def setUpClass(cls) -> None:
        cls.root = tk.Tk()
        cls.root.wait_visibility()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.root.update()
        cls.root.destroy()

    keysyms = {"-": "minus", " ": "space", ":": "colon"}

    def type_in_widget(self, widget: tk.Widget, string: str):
        widget.focus_force()
        for char in string:
            char = self.keysyms.get(char, char)
            self.root.update()
            widget.event_generate(f"<KeyPress-{char}>")
            self.root.update()

    def click_on_widget(self, widget: tk.Widget, x: int, y: int, button: int = 1):
        widget.focus_force()
        self.root.update()
        widget.event_generate(f"<ButtonPress-{button}>", x=x, y=y)
        self.root.update()


class TestValidatedSpinbox(TkTestCase):
    def setUp(self) -> None:
        self.value = tk.DoubleVar()
        self.vsb = w.ValidatedSpinBox(
            self.root, textvariable=self.value, from_=-1, to=10, increment=1
        )
        self.vsb.pack()
        self.vsb.wait_visibility()

    def tearDown(self) -> None:
        self.vsb.destroy()

    def test__key_validate(self):
        # test valid input
        for x in range(10):
            x = str(x)
            p_valid = self.key_validate(x, "")
            n_valid = self.key_validate(x, "-")
            self.assertTrue(p_valid)
            self.assertTrue(n_valid)

            # test letters
            valid = self.key_validate("a")
            self.assertFalse(valid)

            # test non-increment number
            valid = self.key_validate("1", "0.")
            self.assertFalse(valid)

            # test too high number
            valid = self.key_validate("0", "10")
            self.assertFalse(valid)

    def key_validate(self, new, current=""):
        # args are inserted char, insertion index, current value, proposed value, and
        # action code (where '1' is 'insert')
        return self.vsb._key_validate(new, "end", current, current + new, "1")

    def test__key_validate_integration(self):
        self.assertEqual(self.type_in_empty_widget(self.vsb, "10"), "10")
        self.assertEqual(self.type_in_empty_widget(self.vsb, "abcdef"), "")
        self.assertEqual(self.type_in_empty_widget(self.vsb, "200"), "2")

    def type_in_empty_widget(self, widget: tk.Widget, input_sequence: str):
        widget.delete(0, "end")
        super().type_in_widget(widget, input_sequence)
        return widget.get()

    def click_arrow(self, arrow="inc", times=1):
        x = self.vsb.winfo_width() - 5
        y = 5 if arrow == "inc" else 15
        for _ in range(times):
            self.click_on_widget(self.vsb, x=x, y=y)

    def test_arrows(self):
        self.value.set(0)
        self.click_arrow(times=1)
        self.assertEqual(self.vsb.get(), "1")
        self.click_arrow(times=5)
        self.assertEqual(self.vsb.get(), "6")
        self.click_arrow(arrow="dec", times=1)
        self.assertEqual(self.vsb.get(), "5")
        self.click_arrow(times=7)
        self.assertEqual(self.vsb.get(), "10")


class TestValidatedMixin(TkTestCase):
    def setUp(self) -> None:
        class TestClass(w.ValidatedMixin, tk.ttk.Entry):
            pass

        self.vw1 = TestClass(self.root)

    def test__validate(self):
        args = {
            "proposed": "abc",
            "current": "ab",
            "char": "c",
            "event": "key",
            "index": "2",
            "action": "1",
        }
        self.assertTrue(self.vw1._validate(**args))

        fake_key_val = Mock(return_value=False)
        self.vw1._key_validate = fake_key_val
        self.assertFalse(self.vw1._validate(**args))
        fake_key_val.assert_called_with(**args)

        args["event"] = "focusout"
        self.assertTrue(self.vw1._validate(**args))
        fake_focusout_val = Mock(return_value=False)
        self.vw1._focusout_validate = fake_focusout_val
        self.assertFalse(self.vw1._validate(**args))
        fake_focusout_val.assert_called_with(event="focusout")
