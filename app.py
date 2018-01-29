from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
import clearbit

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:postgres123@localhost/social_view'
db=SQLAlchemy(app)

class Data(db.Model):

    __tablename__="data"
    id=db.Column(db.Integer, primary_key=True)
    email_=db.Column(db.String(50))
    avatar_=db.Column(db.String(250))
    fullName_=db.Column(db.String(50))
    city_=db.Column(db.String(30))
    state_=db.Column(db.String(10))
    bio_=db.Column(db.String(250))
    site_=db.Column(db.String(250))
    twitter_=db.Column(db.String(250))
    linkedin_=db.Column(db.String(250))
    facebook_=db.Column(db.String(250))

    def __init__(self, email_, avatar_, fullName_, city_, state_, bio_, site_, twitter_, linkedin_, facebook_):
        self.email_=email_
        self.avatar_=avatar_
        self.fullName_=fullName_
        self.city_=city_
        self.state_=state_
        self.bio_=bio_
        self.site_=site_
        self.twitter_=twitter_
        self.linkedin_=linkedin_
        self.facebook_=facebook_

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/searched", methods=['GET','POST'])
def searched():

    try:
        searched_value = request.form['searched_value']
        clearbit.key = 'sk_78096b7abd95e8d983c836836ce60321'
        response = clearbit.Enrichment.find(email=searched_value, stream=True)

        twitter_url = 'https://www.twitter.com/'
        linkedin_url = 'https://www.linkedin.com/'
        facebook_url = 'https://www.facebook.com/'

        if response['person'] is not None:
          try:
              avatar=response['person']['avatar']
          except:
              avatar=""
          try:
              fullName=response['person']['name']['fullName']
          except:
              fullName=""
          try:
              city=response['person']['geo']['city']
          except:
              city=""
          try:
              state=response['person']['geo']['stateCode']
          except:
              state=""
          try:
              bio=response['person']['bio']
          except:
              bio=""
          try:
              site=response['person']['site']
          except:
              site=""
          try:
              twitter_url += response['person']['twitter']['handle']
          except:
              twitter_url=""
          try:
              linkedin_url += response['person']['linkedin']['handle']
          except:
              linkedin_url=""
          try:
              facebook_url += response['person']['facebook']['handle']
          except:
              facebook_url=""

          # check if email exists in database
          exists = db.session.query(Data).filter_by(email_=searched_value).scalar() is not None

          # if it doesn't, add it to the database
          if exists != True and state is not None:
              data=Data(searched_value,avatar,fullName,city,state,bio,site,twitter_url,linkedin_url,facebook_url)
              db.session.add(data)
              db.session.commit()

          return render_template("searched.html",avatar=avatar,fullName=fullName,
            hometown="  "+city+", "+state,bio=bio,site=site,twitter=twitter_url,
            linkedin=linkedin_url,facebook=facebook_url,searched="mailto:"+searched_value)

    except:
        return render_template("error.html")

@app.route("/history",methods=['GET'])
def history():

    # query all records in the database
    database = db.session.query(Data).all()

    return render_template("history.html",database=database)

if __name__ == '__main__':
    app.debug=True
    app.run()
