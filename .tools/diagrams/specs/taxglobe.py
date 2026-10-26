from svgdiagram import Bars, Flow

PAGE = "work/applications/taxglobe.html"

architecture = (
    Flow("tg-architecture", "TaxGlobe module structure",
         "The form in index.html feeds app.js, which debounces input, calls the pure engine in calc.js and renders "
         "with textContent. calc.js reads the 2023 data in taxData.js. The Node test suite imports calc.js directly.",
         cols=4)
    .node("form", "index.html", "income, province, compare", at=(0, 0), color="cyan")
    .node("app", "app.js", "150 ms debounce, URL state, render with textContent", at=(0, 1), span=2, color="blue")
    .node("cards", "Result cards", "totals, steps, brackets", at=(0, 3), color="cyan")
    .node("calc", "calc.js", "pure engine: brackets, credits, surtax, premium, marginal rate", at=(1, 1), span=2, color="green")
    .node("data", "taxData.js", "2023 brackets and basic personal amounts, 13 jurisdictions", at=(2, 1), span=2, color="yellow")
    .node("tests", "calc.test.js", "Node test runner, 11 tests", at=(1, 3), color="purple")
    .edge("form", "app", "input")
    .edge("app", "cards", "DOM")
    .edge("app", "calc", "calcSummary()")
    .edge("calc", "data", "import")
    .edge("tests", "calc", "import")
)

pipeline = (
    Flow("tg-pipeline", "How one result is calculated",
         "Federal and provincial tax are each worked out on the brackets, then reduced by the basic personal amount "
         "credit. Quebec residents get the 16.5% federal abatement; Ontario adds its surtax and health premium, and "
         "Prince Edward Island its surtax. The two totals add up to the income tax.", cols=4)
    .node("inc", "Taxable income", at=(1, 0), color="cyan")
    .node("fb", "Federal brackets", "5 brackets, 15% to 33%", at=(0, 1), color="blue")
    .node("fc", "Federal credit", "BPA x 15%, phased 15,000 to 13,521", at=(0, 2), color="blue")
    .node("qa", "Quebec abatement", "minus 16.5% of federal tax", at=(0, 3), color="blue")
    .node("tot", "Total income tax", "average rate, next-dollar rate, after-tax income", at=(1, 3), color="green")
    .node("pb", "Provincial brackets", "3 to 8 brackets", at=(2, 1), color="orange")
    .node("pc", "Provincial credit", "BPA x lowest rate", at=(2, 2), color="orange")
    .node("st", "Surtax and premium", "Ontario surtax and health premium, PEI surtax", at=(2, 3), color="orange")
    .edge("inc", "fb").edge("fb", "fc").edge("fc", "qa")
    .edge("inc", "pb").edge("pb", "pc").edge("pc", "st")
    .edge("qa", "tot", "federal tax").edge("st", "tot", "provincial tax")
)

top_rates = (
    Bars("tg-top-rates", "Top combined marginal tax rate, 2023",
         "Federal plus provincial or territorial rate on income over the top bracket, as published for 2023. "
         "TaxGlobe's test suite checks that its engine reproduces every one of these 13 numbers.",
         unit="%", max_value=60)
    .bar("Newfoundland and Labrador", 54.8, color="blue")
    .bar("Nova Scotia", 54.0, color="blue")
    .bar("Ontario", 53.53, "incl. surtax", color="blue")
    .bar("British Columbia", 53.5, color="blue")
    .bar("Quebec", 53.31, "after abatement", color="blue")
    .bar("New Brunswick", 52.5, color="blue")
    .bar("Prince Edward Island", 51.37, "incl. surtax", color="blue")
    .bar("Manitoba", 50.4, color="blue")
    .bar("Alberta", 48.0, color="blue")
    .bar("Yukon", 48.0, color="blue")
    .bar("Saskatchewan", 47.5, color="blue")
    .bar("Northwest Territories", 47.05, color="blue")
    .bar("Nunavut", 44.5, color="blue")
)

DIAGRAMS = [architecture, pipeline, top_rates]
