from flask import Response
from jinja2 import Template

def render_endpoint(endpoint):
  template = Template(endpoint_html)
  return Response(template.render(endpoint.__dict__), mimetype='text/html')

def render_homepage(resource_list_url):
  template = Template(homepage_html)
  conf = {'resource_list_url': resource_list_url}
  return Response(template.render(conf), mimetype='text/html')

homepage_html = """
<!DOCTYPE html>
<html>
<head>
  <title>API Spec</title>
  <link href='//fonts.googleapis.com/css?family=Droid+Sans:400,700' rel='stylesheet' type='text/css'/>
  <link href='http://rantav.github.io/flask-restful-swagger/static/css/hightlight.default.css' media='screen' rel='stylesheet' type='text/css'/>
  <link href='http://rantav.github.io/flask-restful-swagger/static/css/screen.css' media='screen' rel='stylesheet' type='text/css'/>
  <script type="text/javascript" src="http://rantav.github.io/flask-restful-swagger/static/js/all.js" /></script>
  <script type="text/javascript">
    $(function () {
      window.swaggerUi = new SwaggerUi({
      url: "{{resource_list_url}}",
      dom_id: "swagger-ui-container",
      supportedSubmitMethods: ['get', 'post', 'put', 'delete'],
      onComplete: function(swaggerApi, swaggerUi){
        if(console) {
          console.log("Loaded SwaggerUI")
        }
        $('pre code').each(function(i, e) {hljs.highlightBlock(e)});
      },
      onFailure: function(data) {
        if(console) {
          console.log("Unable to Load SwaggerUI");
          console.log(data);
        }
      },
      docExpansion: "none"
    });
    $('#input_apiKey').change(function() {
      var key = $('#input_apiKey')[0].value;
      console.log("key: " + key);
      if(key && key.trim() != "") {
        console.log("added key " + key);
        window.authorizations.add("key", new ApiKeyAuthorization("api_key", key, "query"));
      }
    })
    window.swaggerUi.load();
  });
  </script>
  <style type="text/css">
    ul.links a {
      line-height: 25px;
      color: #fff;
      font-weight: bolder;
      text-decoration: none;
    }
    ul.links a:hover {
      text-decoration: underline;
    }
    ul.links li:before {
     color: #fff;
     content: "\00BB";
    }
  </style>
</head>
<body>
<div id='header'>
  <div class="swagger-ui-wrap">
    <a id="logo" href="http://swagger.wordnik.com">swagger</a>
    <form id='api_selector'>
      <div class='input icon-btn'>
        <img id="show-wordnik-dev-icon" src="http://rantav.github.io/flask-restful-swagger/static/images/wordnik_api.png" title="Show Wordnik Developer Apis">
      </div>
      <div class='input'><input placeholder="http://example.com/api" id="input_baseUrl" name="baseUrl" type="text"/></div>
      <div class='input'><input disabled='disabled' placeholder="api_key" id="input_apiKey" name="apiKey" type="text"/></div>
      <div class='input'><a id="explore" href="#">Explore</a></div>
    </form>
  </div>
</div>
<div id="message-bar" class="swagger-ui-wrap">&nbsp;</div>
<div id="swagger-ui-container" class="swagger-ui-wrap"></div>
</body>
</html>
"""

endpoint_html = """
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Api Docs for {{path}}</title>
    <link rel="stylesheet" href="//netdna.bootstrapcdn.com/bootstrap/3.0.3/css/bootstrap.min.css">
    <style>
      body {margin-top: 60px;}
    </style>
  </head>
  <body>
    <nav class="navbar navbar-inverse navbar-fixed-top" role="navigation">
      <div class="container">
        <div class="navbar-header">
          <button type="button" class="navbar-toggle" data-toggle="collapse" data-target=".navbar-ex1-collapse">
            <span class="sr-only">Toggle navigation</span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
          </button>
        </div>
        <!-- Collect the nav links, forms, and other content for toggling -->
        <div class="collapse navbar-collapse navbar-ex1-collapse">
          <ul class="nav navbar-nav">
            {% for operation in operations %}
              <li><a href="#{{operation.method}}">{{operation.method}}</a></li>
            {% endfor %}
          </ul>
        </div><!-- /.navbar-collapse -->
      </div><!-- /.container -->
    </nav>
    <div class="container">
      <div class="row">
        <div class="col-lg-12">
          <h1>{{path}}</h1>
          <p class='lead'>{{description if description != None}}</p>
        </div>
        <div class="col-lg-12">
        {% for operation in operations %}
          <div class="panel panel-success" id='{{operation.method}}'>
            <div class="panel-heading">
              <h3 class="panel-title">{{operation.method}}</h3>
              <p>{{operation.summary if operation.summary != None}}</p>
            </div>
            <div class="panel-body">
              {% if operation.parameters %}
                <h4>Parameters</h4>
                <dl>
                  {% for parameter in operation.parameters %}
                    <dt>
                      {{parameter.name}}
                      {% if parameter.description %}
                        - {{parameter.description}}
                      {% endif %}
                    </dt>
                    <dd>Type: {{parameter.dataType}}</dd>
                    <dd>Allow Multiple: {{parameter.allowMultiple}}</dd>
                    <dd>Required: {{parameter.required}}</dd>
                  {% endfor %}
                </dl>
              {% endif %}
              {% if operation.notes %}
                <p><strong>Implementation notes</strong>: {{operation.notes}}</p>
              {% endif %}
              {% if operation.responseClass %}
                <p><strong>Response Class</strong>: {{operation.responseClass}}</p>
              {% endif %}
            </div>
          </div>
        {% endfor %}
      </div>
    </div><!-- /.container -->
    <script src="//cdnjs.cloudflare.com/ajax/libs/jquery/2.0.3/jquery.min.js"></script>
    <script src="//netdna.bootstrapcdn.com/bootstrap/3.0.3/js/bootstrap.min.js"></script>
  </body>
</html>
"""
