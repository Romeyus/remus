import os
from typing import Any

from remus import panic

try:
    import jinja2

except ImportError:
    panic("missing dependency, install 'remus[html]'")


# ==========================================
# ===            Templates                 ===
# ==========================================
class Templates:
    def __init__(self, *directories: str | os.PathLike[str]) -> None:
        self._env = jinja2.Environment(
            autoescape=True, loader=jinja2.FileSystemLoader(directories)
        )

    def render(self, name: str, **context: Any) -> str:
        return self._env.get_template(name).render(**context)
