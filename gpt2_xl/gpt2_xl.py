import pynecone as pc
import requests

with open("bearer.txt", "r") as f:
    bearer = f.read()

API_URL = "https://api-inference.huggingface.co/models/gpt2-xl"
headers = {"Authorization": bearer}

x = 0


def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    return response.json()


init = query({"inputs": "Hello World"})


class CopyToClipboard(pc.Component):
    """Component to copy text to clipboard."""

    library = "react-copy-to-clipboard"

    tag = "CopyToClipboard"

    # The text to copy when clicked.
    text: pc.Var[str]

    @classmethod
    def get_triggers(cls) -> set[str]:
        return super().get_triggers() | {"on_copy"}


copy_to_clipboard = CopyToClipboard.create


class TextareaState(pc.State):
    text: str


class State(pc.State):
    """The app state."""

    prompt = ""
    generate_text = ""
    text_processing = False
    text_made = False

    def process_text(self):
        self.text_processing = True
        self.text_made = False

    def get_text(self):
        global x
        response = query(
            {
                "inputs": self.prompt,
            }
        )
        try:
            self.generate_text = response[0]["generated_text"]
        except KeyError:
            self.generate_text = str(response)
        self.text_processing = False
        self.text_made = True
        x = 0

    def clear_text(self):
        self.generate_text = ""
        self.text_processing = True
        self.text_made = False

    def clear_text_no_bar(self):
        self.generate_text = ""
        self.text_processing = False
        self.text_made = False


style = {
    "text_align": "center",
}


def index():
    return pc.center(
        pc.vstack(
            pc.heading("GPT2-XL", size="lg"),
            pc.text_area(
                placeholder="Enter a sentence..",
                width="80%",
                shadow="md",
                on_blur=State.set_prompt,
            ),
            pc.button(
                "Generate",
                on_click=[State.clear_text, State.process_text, State.get_text],
                width="80%",
                shadow="md",
            ),
            pc.cond(
                State.text_processing,
                pc.circular_progress(is_indeterminate=True),
                pc.cond(
                    State.text_made,
                    pc.vstack(
                        pc.divider(),
                        pc.heading("Output", size="md"),
                        pc.box(
                            pc.text(
                                State.generate_text,
                            ),
                            border_radius="xl",
                            border="1px solid #e2e8f0",
                            width="80%",
                            padding="1em",
                            shadow="md",
                        ),
                        pc.hstack(
                            pc.button(
                                "Clear",
                                on_click=[State.clear_text_no_bar],
                                width="50%",
                                shadow="md",
                            ),
                            copy_to_clipboard(
                                pc.button(
                                    "Copy",
                                    width="50%",
                                    shadow="md",
                                ),
                                text=pc.Var.create(State.generate_text, is_string=True),
                            ),
                            width="80%",
                        ),
                        width="100%",
                    ),
                ),
            ),
            pc.divider(),
            pc.box(
                "Made by ",
                pc.link(
                    "Rohan Arni", href="https://rohanarni.com", color="rgb(107,99,246)"
                ),
                " with ",
                pc.link(
                    "Pynecone", href="https://pynecone.io", color="rgb(107,99,246)"
                ),
                " and the ",
                pc.link(
                    "Hugging Face API",
                    href="https://huggingface.co",
                    color="rgb(107,99,246)",
                ),
                ".",
            ),
            bg="white",
            padding="2em",
            shadow="md",
            border_radius="lg",
            width="40%",
        ),
        width="100%",
        height="100vh",
        bg="radial-gradient(circle at 22% 11%,rgba(62, 180, 137,.20),hsla(0,0%,100%,0) 19%)",
    )


# Add state and page to the app.
app = pc.App(state=State)
app.add_page(index, title="GPT2-XL")
app.compile()
