"""Azure Functions entry points for Thungatha Scout."""

import azure.functions as func

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


@app.route(route="health", methods=["GET"], auth_level=func.AuthLevel.ANONYMOUS)
def health(_: func.HttpRequest) -> func.HttpResponse:
    """Report that the Functions host can invoke the Scout app."""
    return func.HttpResponse(
        body='{"status":"healthy"}',
        status_code=200,
        mimetype="application/json",
    )
