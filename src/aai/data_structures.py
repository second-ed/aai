import os

import attr
import nbformat
from attr.validators import deep_iterable, instance_of, optional
from black import InvalidInput

from . import utils


@attr.define
class MarkdownPoint:
    unit: list[int] = attr.ib(
        validator=[instance_of(list)], converter=utils.convert_unit
    )
    point: str = attr.ib(validator=[instance_of(str)])
    source: str | None = attr.ib(
        default=None, validator=[optional(instance_of(str))]
    )

    def create_source_link(self, refs: dict) -> str:
        mod_point = self.point.strip(".")
        mod_point = mod_point[:1].upper() + mod_point[1:]
        if self.source:
            i = utils.get_ref_number(refs, self)
            return f"{mod_point} [[{i}]]({self.source}). "
        return f"{mod_point}. "


@attr.define
class CodeSnippet:
    unit: list[int] = attr.ib(
        validator=[instance_of(list)], converter=utils.convert_unit
    )
    snippet: str = attr.ib(
        validator=[instance_of(str)], converter=utils.format_code_string
    )
    source: str | None = attr.ib(
        default=None, validator=[optional(instance_of(str))]
    )


@attr.define
class ImageLink:
    unit: list[int] = attr.ib(
        validator=[instance_of(list)], converter=utils.convert_unit
    )
    point: str = attr.ib(validator=[instance_of(str)])
    source: str | None = attr.ib(
        default=None, validator=[optional(instance_of(str))]
    )

    def create_source_link(self, refs: dict) -> str:
        mod_point = f"![image]({self.point})"
        if self.source:
            i = utils.get_ref_number(refs, self)
            return f"{mod_point} [[{i}]]({self.source})\n\n"
        return f"{mod_point}\n\n"


@attr.define
class Module:
    points: list[MarkdownPoint | CodeSnippet | ImageLink] = attr.ib(
        validator=[
            deep_iterable(
                member_validator=instance_of(
                    (MarkdownPoint, CodeSnippet, ImageLink)
                ),
                iterable_validator=instance_of(list),
            )
        ]
    )
    refs: dict = attr.ib(default=None, validator=[optional(instance_of(dict))])  # type: ignore
    cells: list = attr.ib(default=None, validator=[optional(instance_of(list))])  # type: ignore
    notebook: nbformat.NotebookNode = attr.ib(
        default=nbformat.v4.new_notebook()
    )
    unit: str | None = attr.ib(
        default=None, validator=[optional(instance_of(str))]
    )

    def __attrs_post_init__(self) -> None:
        self.refs = {}
        self.cells = []

    def populate_cells(self):
        for item in self.points:
            self.set_curr_unit(item.unit)
            if isinstance(item, CodeSnippet):
                self.cells.append(
                    nbformat.v4.new_code_cell(
                        f"# source: {item.source}\n" + item.snippet
                    )
                )

            if isinstance(item, (MarkdownPoint, ImageLink)):
                self.cells.append(
                    nbformat.v4.new_markdown_cell(
                        item.create_source_link(self.refs)
                    )
                )

    def get_bib(self):
        bib = ["\n\n## References"]

        for link, ref in self.refs.items():
            bib.append(f"[{ref}] {link}")

        self.cells.append(nbformat.v4.new_markdown_cell("\n\n".join(bib)))

    def set_curr_unit(self, unit) -> None:
        curr_unit = ".".join(list(map(str, unit)))
        if curr_unit != self.unit:
            self.cells.append(nbformat.v4.new_markdown_cell(f"# {curr_unit}"))
            self.unit = curr_unit

    def generate_notebook(self):
        self.populate_cells()
        self.get_bib()
        self.notebook["cells"] = self.cells
        out_folder = utils.get_dir_path(__file__, 2, "outputs/nbs")
        os.makedirs(out_folder, exist_ok=True)
        filename: str = "aai_notebook"
        nbformat.write(self.notebook, f"{out_folder}/{filename}.ipynb")


def create_markdown_point(
    unit_code, text: str, source: str | None
) -> MarkdownPoint:
    return MarkdownPoint(str(unit_code), text, source)


def create_code_snippet(
    unit_code, code_snippet: str, source: str | None
) -> CodeSnippet | None:
    try:
        return CodeSnippet(str(unit_code), code_snippet, source)
    except InvalidInput as e:
        print(f"{e} for {code_snippet}")


def create_image_link(unit_code, text: str, source: str | None) -> ImageLink:
    return ImageLink(str(unit_code), text, source)
