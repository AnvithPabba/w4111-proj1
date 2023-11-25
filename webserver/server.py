
"""
Columbia's COMS W4111.001 Introduction to Databases
Example Webserver
To run locally:
    python3 server.py
Go to http://localhost:8111 in your browser.
A debugger such as "pdb" may be helpful for debugging.
Read about it online.
"""
import os
  # accessible as a variable in index.html:
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, abort, session, url_for

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)
app.secret_key = '1234567'

#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of:
#
#     postgresql://USER:PASSWORD@34.75.94.195/proj1part2
#
# For example, if you had username gravano and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://gravano:foobar@34.75.94.195/proj1part2"
#
DATABASEURI = "postgresql://nj2513:061380@34.74.171.121/proj1part2"


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. This is only an example showing you how to run queries in your database using SQLAlchemy.
#
conn = engine.connect()

# The string needs to be wrapped around text()

# conn.execute(text("""CREATE TABLE IF NOT EXISTS test (
#   id serial,
#   name text
# );"""))
# conn.execute(text("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');"""))

# To make the queries run, we need to add this commit line

conn.commit() 

@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print("uh oh, problem connecting to database")
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
#
# see for routing: https://flask.palletsprojects.com/en/2.0.x/quickstart/?highlight=routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: https://flask.palletsprojects.com/en/2.0.x/api/?highlight=incoming%20request%20data

  """

  # DEBUG: this is debugging code to see what request looks like
  # print(request.args)



  #
  # example of a database query 
  #
  # cursor = g.conn.execute(text("SELECT name FROM test"))
  # g.conn.commit()

  # # 2 ways to get results

  # # Indexing result by column number
  # names = []
  # for result in cursor:
  #   names.append(result[0])  

  # # Indexing result by column name
  # names = []
  # results = cursor.mappings().all()
  # for result in results:
  #   names.append(result["name"])
  # cursor.close()

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/primer-on-jinja-templating/
  #
  # You can see an example template in templates/index.html
  #
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be
  # accessible as a variable in index.html:
  #
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
  #
  #     # creates a <div> tag for each element in data
  #     # will print:
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  #
  # context = dict(data = names)


  


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #
  return render_template("index.html")#, **context)

@app.route('/logging_out')
def logging_out():
  session.clear()
  return redirect("/")
  






@app.route('/models')
def view_models():

  cursor = conn.execute(text("SELECT model_id,model_name,num_downloads FROM user_uploads_model_with_citation ORDER BY num_downloads DESC"))
  conn.commit()

  temp = []

  for row in cursor:
    temp.append((row[0],row[1],row[2]))

  return render_template("models.html", temp=temp)





@app.route('/datasets')
def view_datasets():

  cursor = conn.execute(text("SELECT dataset_id,dataset_name FROM user_uploads_dataset_with_citation"))
  conn.commit()

  temp = []

  for row in cursor:
    temp.append((row[0],row[1]))

  return render_template("datasets.html", temp=temp)


@app.route('/citations')
def view_citations():

  cursor = conn.execute(text("SELECT * FROM citations"))
  conn.commit()

  temp = []

  for row in cursor:
    temp.append(row)

  return render_template("citations.html", temp=temp)






@app.route('/login', methods = ["GET", "POST"])
def view_login():

  if request.method == "POST":

    # print(request.form.get("username"))
    # print(request.form.get("password"))
    username = request.form.get("username")
    password = request.form.get("password")
    params = {'username':username, 'password':password}
    query = text("SELECT username,password FROM customer WHERE username = :username and password = :password")
    cursor = conn.execute(query, params)
    conn.commit() 


    if cursor.rowcount == 0:
      return render_template("login.html", error = "Invalid credentials")
    else:
      session['username']=request.form.get("username")
      return redirect("/postlogin")


  return render_template("login.html")






@app.route('/postlogin')
def view_postlogin():
  username = session['username']
  return render_template("postlogin.html", username=username)






@app.route('/models/<model_id>')
def view_specific_model(model_id):

  query = text("SELECT * FROM user_uploads_model_with_citation M INNER JOIN citations C ON M.citation_id = C.citation_id WHERE M.model_id = :model_id")
  params = {'model_id': model_id}
  cursor = conn.execute(query, params)
  conn.commit()

  record = cursor.fetchone()

  temp = []

  headings = ['model_id', 'model_name', 'num_parameters', 'num_layers', 'tag1', 'tag2', 'tag3', 'num_downloads', 'username', 'citation_id', 'citation_id', "author1"   ,    "author2"    , "year_published" , "conference"]
  
  for i in range(len(record)):
    if i!=9:
      temp.append((headings[i], record[i]))

  

  query = text("SELECT * FROM logs_versionhistory WHERE model_id = :model_id")
  params = {'model_id': model_id}
  cursor = conn.execute(query, params)
  conn.commit()

  revs = []

  for i in cursor:
    revs.append((i))

  context = dict(temp = temp, revs = revs)

  return render_template("view_model_info.html", **context)





@app.route('/datasets/<dataset_id>')
def view_specific_dataset(dataset_id):

  query = text("SELECT * FROM user_uploads_dataset_with_citation M INNER JOIN citations C ON M.citation_id = C.citation_id WHERE M.dataset_id = :dataset_id")
  params = {'dataset_id': dataset_id}
  cursor = conn.execute(query, params)
  conn.commit()

  record = cursor.fetchone()

  temp = []

  headings = ["dataset_id","dataset_name","num_data_points","num_features","description","tag1","tag2","tag3","username","citation_id","citation_id","author1","author2","year_published","conference"]
  
  for i in range(len(record)):
    if i!=9:
      temp.append((headings[i], record[i]))

  
  
  query = text("SELECT * FROM user_reviews_dataset WHERE dataset_id = :dataset_id")
  params = {'dataset_id': dataset_id}
  cursor = conn.execute(query, params)
  conn.commit()

  revs = []

  for i in cursor:
    revs.append((i))

  context = dict(temp = temp, revs = revs)

  return render_template("view_dataset_info.html", **context)

@app.route('/upload_model_page')
def upload_model_page():
  return render_template("upload_model_form.html")

@app.route('/upload_model', methods = ["POST"])
def upload_model():

  model_id = request.form.get("model_id")
  model_name = request.form.get("model_name")
  num_parameters = request.form.get("num_parameters")
  num_layers = request.form.get("num_layers")
  tag1 = request.form.get("tag1")
  tag2 = request.form.get("tag2")
  tag3 = request.form.get("tag3")
  num_downloads = request.form.get("num_downloads")
  username = request.form.get("username")
  citation_id = request.form.get("citation_id")

  params_dict = {
        "model_id": model_id,
        "model_name": model_name,
        "num_parameters": num_parameters,
        "num_layers": num_layers,
        "tag1": tag1,
        "tag2": tag2,
        "tag3": tag3,
        "num_downloads": num_downloads,
        "username": username,
        "citation_id": citation_id
    }

  query = text("INSERT INTO user_uploads_model_with_citation (model_id, model_name, num_parameters, num_layers, tag1, tag2, tag3, num_downloads, username, citation_ID) VALUES (:model_id, :model_name, :num_parameters, :num_layers, :tag1, :tag2, :tag3, :num_downloads, :username, :citation_id)")

  conn.execute(query, params_dict)
  conn.commit()

  return redirect('/models')

  

@app.route('/upload_dataset_page')
def upload_dataset_page():
    return render_template("upload_dataset_form.html")

@app.route('/upload_dataset', methods=["POST"])
def upload_dataset():
    dataset_id = request.form.get("dataset_id")
    dataset_name = request.form.get("dataset_name")
    num_data_points = request.form.get("num_data_points")
    num_features = request.form.get("num_features")
    description = request.form.get("description")
    tag1 = request.form.get("tag1")
    tag2 = request.form.get("tag2")
    tag3 = request.form.get("tag3")
    username = request.form.get("username")
    citation_id = request.form.get("citation_id")

    params_dict = {
        "dataset_id": dataset_id,
        "dataset_name": dataset_name,
        "num_data_points": num_data_points,
        "num_features": num_features,
        "description": description,
        "tag1": tag1,
        "tag2": tag2,
        "tag3": tag3,
        "username": username,
        "citation_id": citation_id
    }

    query = text("INSERT INTO user_uploads_dataset_with_citation (dataset_id, dataset_name, num_data_points, num_features, description, tag1, tag2, tag3, username, citation_id) VALUES (:dataset_id, :dataset_name, :num_data_points, :num_features, :description, :tag1, :tag2, :tag3, :username, :citation_id)")

    conn.execute(query, params_dict)
    conn.commit()

    return redirect('/datasets')




@app.route('/upload_citation_page')
def upload_citation_page():
    return render_template("upload_citation_form.html")

@app.route('/upload_citation', methods=["POST"])
def upload_citation():
    citation_id = request.form.get("citation_id")
    author1 = request.form.get("author1")
    author2 = request.form.get("author2")
    year_published = request.form.get("year_published")
    conference = request.form.get("conference")

    params_dict = {
        "citation_id": citation_id,
        "author1": author1,
        "author2": author2,
        "year_published": year_published,
        "conference": conference
    }

    query = text("INSERT INTO citations (citation_id, author1, author2, year_published, conference) VALUES (:citation_id, :author1, :author2, :year_published, :conference)")

    conn.execute(query, params_dict)
    conn.commit()

    return redirect('/citations')

@app.route('/upload_review_page')
def upload_review_page():
    return render_template("upload_review_form.html")

@app.route('/upload_dataset_review', methods=["POST"])
def upload_dataset_review():
    review_id = request.form.get("review_id")
    date_written = request.form.get("date_written")
    written_review = request.form.get("written_review")
    rating = request.form.get("rating")
    username = request.form.get("username")
    dataset_id = request.form.get("dataset_id")

    params_dict = {
        "review_id": review_id,
        "date_written": date_written,
        "written_review": written_review,
        "rating": rating,
        "username": username,
        "dataset_id": dataset_id
    }

    query = text("INSERT INTO user_reviews_dataset (date_written, Review_ID, written_review, rating, Username, Dataset_ID) VALUES (:date_written, :review_id, :written_review, :rating, :username, :dataset_id)")

    conn.execute(query, params_dict)
    conn.commit()

    return redirect(url_for('view_specific_dataset', dataset_id = dataset_id))

  


@app.route('/upload_version_for_model/<model_id>')
def upload_version_for_model(model_id):

    return render_template("upload_model_version_form.html", model_id = model_id)

@app.route('/upload_version_history/<model_id>', methods=["POST"])
def upload_version_history(model_id):
    time_stamp = request.form.get("time_stamp")
    version = request.form.get("version")


    params_dict = {
        "model_id": model_id,
        "time_stamp": time_stamp,
        "version": version
    }

    query = text("INSERT INTO logs_versionhistory (model_id, time_stamp, version) VALUES (:model_id, :time_stamp, :version)")

    conn.execute(query, params_dict)
    conn.commit()

    return redirect(url_for('view_specific_model', model_id = model_id))



  


















#
# This is an example of a different path.  You can see it at:
#
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#
# @app.route('/another')
# def another():
#   return render_template("another.html")


# Example of adding new data to the database
# @app.route('/add', methods=['POST'])
# def add(): 
#   name = request.form['name']
#   params_dict = {"name":name}
#   g.conn.execute(text('INSERT INTO test(name) VALUES (:name)'), params_dict)
#   g.conn.commit()
#   return redirect('/')


# @app.route('/login')
# def login():
#     abort(401)
#     this_is_never_executed()


if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)
  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python3 server.py

    Show the help text using:

        python3 server.py --help

    """

    HOST, PORT = host, port
    print("running on %s:%d" % (HOST, PORT))
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

  run()
