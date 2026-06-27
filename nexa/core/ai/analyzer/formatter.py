from .schema import AnalysisReport

class OutputFormatter:
    """
    Renders AnalysisReport into the requested string format.
    """
    def format(self, report: AnalysisReport, fmt: str) -> str:
        fmt = fmt.lower()
        if fmt == "json":
            return report.to_json()
        elif fmt == "markdown":
            return report.to_markdown()
        elif fmt == "html":
            return report.to_html()
        else:
            return report.to_text()
