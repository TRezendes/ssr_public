# Simple Summer Reading #

## by [Timothy Rezendes](https://www.rezendes.info "Rezendes.info") ##

This is an early development version of *Simple Summer Reading*, a web app for public library Summer Reading programs.  
<br />  

## *requirements_update* branch

Flask and its dependencies and SQLAlchemy have undergone some fairly significant changes since this repository was originally published, and the app needs some massaging to account for the updates.

 1. Flask
    - Updated 5/17/2023. Flask & Werkzeug have been updated to the current versions—2.3.2 and 2.3.4, respectively. Flask-Login and Flask-WTF have also been updated to maintain compatibility with the updated Flask. So far, everthing seems to be working as expected.

 2. SQLAlchemy
    - Not Yet Updated. The SQLAlchemy 1.4 to 2.0 transition was a major change and will likely require a rewrite of most, if not all, of the code that interacts with the database. It should be a relatively minor rewrite but, nevertheless, one I do not have time to undertake at the moment. It is on my radar, though, and I will endeavor to make the effort soon.  
<br />

---

<br />

![GitHub](https://img.shields.io/github/license/TRezendes/ssr_public)
