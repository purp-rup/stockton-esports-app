from EsportsManagementTool import app

@app.route('/example')
def example():
    return "This is a view function outside of __init__.py"