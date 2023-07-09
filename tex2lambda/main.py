"""The main input for tex2lambda, defining both the CLT and main library function."""

import importlib

import panflute as pf
import rich_click as click

from tex2lambda import question
from tex2lambda.json_convert import json_convert


def main(tex_file: str, subject: str, output_dir: str = "out") -> question.Questions:
    """Takes in a TeX file for a given subject and produces Lambda Feedback compatible json/zip files.

    Args:
        tex_file: The absolute path to a TeX file.
        subject: The subject which the TeX file contains questions for.
        output_dir: An optional argument for where to output the json/zip files. Defaults to `./out`

    Returns:
        A list of questions and how they would be broken down into different Lambda Feedback sections
        in a Python-readable format.
    """
    # The list of questions for Lambda Feedback as a Python API.
    # See `tex2lambda.question` for the full structure of Questions()
    questions = question.Questions()

    # Dynamically import the correct pandoc filter depending on the subject.
    subject_module = importlib.import_module(f"tex2lambda.subjects.{subject.lower()}")

    with open(tex_file, "r", encoding="utf-8") as file:
        text = file.read()

    # Parse the Pandoc AST using the relevant panflute filter.
    pf.run_filter(
        subject_module.pandoc_filter,
        doc=pf.convert_text(text, input_format="latex", standalone=True),
        questions=questions,
        tex_file=tex_file,
    )

    # Read the Python API format and convert to JSON.
    json_convert.main(questions.questions, output_dir)

    return questions


@click.command(
    epilog="See the docs at https://lambda-feedback.github.io/user-documentation/ for more details."
)
@click.argument(  # Use resolve_path to get absolute path
    "tex_file", type=click.Path(exists=True, readable=True, resolve_path=True)
)
@click.argument("subject")
@click.option(
    "--out",
    "-o",
    "output_dir",
    default="out",
    help="Directory to output json/zip files to.",
    type=click.Path(resolve_path=True),
)
def click(tex_file: str, subject: str, output_dir: str) -> None:
    """Takes in a TEX_FILE for a given SUBJECT and produces Lambda Feedback compatible json/zip files."""
    # main() is made separate from click() so that it can be easily imported as part of a library.
    main(tex_file, subject, output_dir)


if __name__ == "__main__":
    click()
