import subprocess
import os
from tempfile import TemporaryDirectory


def generate_latex_table(sequence, decimal, algebraic, continued_fraction):
    latex_content = (
        r"""\documentclass{article}
\usepackage{amsmath}
\usepackage{amsfonts}
\usepackage{graphicx}
\pagestyle{empty} % Suppress page numbering
\begin{document}

\begin{table}[h]
\centering
\begin{tabular}{ll}
Sequence      & """
        + sequence
        + r""" \\\\
Decimal       & """
        + decimal
        + r""" \\\\
Algebraic form & """
        + algebraic
        + r""" \\\\
Continued fraction & """
        + continued_fraction
        + r"""
\end{tabular}
\end{table}

\end{document}
"""
    )
    return latex_content


def create_continued_fraction_str(seq):
    # Start the LaTeX string with the first element of the sequence
    continued_fraction_str = r"\(" + str(seq[0])
    # Check if the sequence has more than one element
    if len(seq) > 1:
        # Limit the display to the first 4 elements (after the first) if the sequence is longer than 5
        display_seq = seq[1:5] if len(seq) > 5 else seq[1:]
        # Add the sequence elements to the continued fraction string
        for num in display_seq:
            continued_fraction_str += f" + \\frac{{1}}{{{num}"
        # Close the brackets for the displayed sequence
        continued_fraction_str += (
            " + \\ddots" if len(seq) > 5 else "}" * len(display_seq)
        )
    # End the LaTeX math mode
    continued_fraction_str += r"\)"
    return continued_fraction_str


def create_image_from_latex(match, output_directory):
    seq, key, value = match
    decimal_str = f"{value:.8f}..."

    sequence_str = ", ".join(map(str, seq))

    # Generate the algebraic form string
    a, b, c = key
    algebraic_str = (
        r"\(" + r"\frac{" + f"{a} + \sqrt{{{b}}}" + r"}{" + f"{c}" + r"}" + r"\)"
    )

    # Generate the continued fraction string
    continued_fraction_str = create_continued_fraction_str(seq)

    # Call the existing function to generate the LaTeX document and convert it to an image
    with TemporaryDirectory() as tmpdir:
        # Set file paths
        tex_file = os.path.join(tmpdir, "table.tex")
        dvi_file = "table.dvi"
        cropped_pdf_file = "table-cropped.pdf"
        output_png_file = os.path.join(output_directory, f"table_{seq}_{key}.png")

        # Create the LaTeX content
        latex_content = generate_latex_table(
            sequence_str, decimal_str, algebraic_str, continued_fraction_str
        )

        # Write to a .tex file in the temporary directory
        with open(tex_file, "w") as file:
            file.write(latex_content)

        # Compile the LaTeX file to DVI
        subprocess.run(["latex", "-output-directory", tmpdir, tex_file])

        # Convert the DVI to PDF
        subprocess.run(
            [
                "dvipdf",
                os.path.join(tmpdir, dvi_file),
                os.path.join(tmpdir, "table.pdf"),
            ]
        )

        # Crop the PDF to the size of the table
        subprocess.run(
            [
                "pdfcrop",
                os.path.join(tmpdir, "table.pdf"),
                os.path.join(tmpdir, cropped_pdf_file),
            ]
        )

        # Convert the cropped PDF to an image
        subprocess.run(
            [
                "convert",
                "-density",
                "300",
                "-background",
                "white",
                "-flatten",
                os.path.join(tmpdir, cropped_pdf_file),
                output_png_file,
            ]
        )


if __name__ == "__main__":
    output_directory = "output"
    os.makedirs(output_directory, exist_ok=True)

    seq = (1, 1, 1)
    key = (1, 5, 2)
    value = 1.618033988749894

    data = [(seq, key, value)]

    for match in data:
        create_image_from_latex(match, output_directory)
