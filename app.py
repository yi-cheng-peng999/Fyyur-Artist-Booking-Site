#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import datetime
import sys
from flask import render_template, request, flash, redirect, url_for, jsonify
import logging
from logging import Formatter, FileHandler
from forms import *
from models import db, Venue, Artist, Show
from config import app, format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # DONE: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  city_state_venue = {}
  venues = Venue.query.order_by(Venue.id).all()
  for venue in venues:
    city_state = (venue.city, venue.state)
    if city_state not in city_state_venue:
      city_state_venue[city_state] = []

    cnt = Show.query.filter(Show.venue_id == venue.id, Show.start_time > datetime.now()).count()
    query_result = {
      'id': venue.id,
      'name': venue.name,
      'num_upcoming_shows': cnt
    }
    city_state_venue[city_state].append(query_result)

  result = []
  for city_state, venue_list in city_state_venue.items():
    result.append({
      'city': city_state[0],
      'state': city_state[1],
      'venues': venue_list
    })

  return render_template('pages/venues.html', areas=result)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  search_term = '%'+request.form['search_term']+'%'
  venues = Venue.query.with_entities(Venue.id, Venue.name).filter(Venue.name.ilike(search_term)).all()
  result = {
    'count': len(venues)
  }
  def venue_transform(v):
    return {
      'id': v.id,
      'name': v.name
    }
  venues = list(map(venue_transform, venues))
  for venue in venues:
    venue['num_upcoming_shows'] = Show.query.filter(Show.artist_id == venue['id'], Show.start_time > datetime.now())\
      .count()
  result['data'] = venues

  return render_template('pages/search_venues.html', results=result, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # DONE: replace with real venue data from the venues table, using venue_id
  data = Venue.query.get(venue_id)
  if data:
    data.past_shows = []
    data.upcoming_shows = []
    for show in data.shows:
      show.artist_name = show.artist.name
      show.artist_image_link = show.artist.image_link
      if show.start_time > datetime.now():
        show.start_time = format_datetime(str(show.start_time))
        data.upcoming_shows.append(show)
      else:
        show.start_time = format_datetime(str(show.start_time))
        data.past_shows.append(show)

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # DONE: insert form data as a new Venue record in the db, instead
  # DONE: modify data to be the data object returned from db insertion
  try:
    form = VenueForm(request.form)
    venue = Venue()
    form.populate_obj(venue)
    db.session.add(venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully created!')
  except:
    # DONE: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Venue ' + request.form['name'] + ' could not be created.')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # DONE: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  try:
    venue = Venue.query.get(venue_id)
    db.session.delete(venue)
    db.session.commit()
    message = 'Delete success.'
  except Exception as e:
    db.session.rollbock()
    message = 'Delete failed. ' + e
  finally:
    db.session.close()

  return jsonify({ 'message': message })

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # DONE: replace with real data returned from querying the database
  artists = Artist.query.with_entities(Artist.id, Artist.name).order_by(Artist.id).all()
  def artist_transform(a):
    return {
      'id': a.id,
      'name': a.name
    }
  data = list(map(artist_transform, artists))

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # DONE: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_term = '%'+request.form['search_term']+'%'
  artists = Artist.query.with_entities(Artist.id, Artist.name).filter(Artist.name.ilike(search_term)).all()
  result = {
    'count': len(artists)
  }
  def artist_transform(a):
    return {
      'id': a.id,
      'name': a.name
    }
  artists = list(map(artist_transform, artists))
  for artist in artists:
    artist['num_upcoming_shows'] = Show.query.filter(Show.artist_id == artist['id'], Show.start_time > datetime.now())\
      .count()
  result['data'] = artists

  return render_template('pages/search_artists.html', results=result, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # DONE: replace with real artist data from the artist table, using artist_id
  data = Artist.query.get(artist_id)
  if data:
    data.past_shows = []
    data.upcoming_shows = []
    for show in data.shows:
      show.venue_name = show.venue.name
      show.venue_image_link = show.venue.image_link
      if show.start_time > datetime.now():
        show.start_time = format_datetime(str(show.start_time))
        data.upcoming_shows.append(show)
      else:
        show.start_time = format_datetime(str(show.start_time))
        data.past_shows.append(show)

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = vars(Artist.query.get(artist_id))
  form.genres.data = [(genre) for genre in artist['genres']]

  # DONE: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # DONE: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  try:
    artist = Artist.query.get(artist_id)
    form = ArtistForm()
    artist.name = form.name.data
    artist.city = form.city.data
    artist.state = form.state.data
    artist.phone = form.phone.data
    artist.genres = form.genres.data
    artist.image_link = form.image_link.data
    artist.facebook_link = form.facebook_link.data
    artist.website_link = form.website_link.data
    artist.seeking_venue = form.seeking_venue.data
    artist.seeking_description = form.seeking_description.data
    db.session.commit()
  except Exception as e:
    flash(e)
    db.session.rollback()
  finally:
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue = vars(Venue.query.get(venue_id))
  form.genres.data = [(genre) for genre in venue['genres']]

  # DONE: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # DONE: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  try:
    venue = Venue.query.get(venue_id)
    form = VenueForm()
    venue.name = form.name.data
    venue.city = form.city.data
    venue.state = form.state.data
    venue.address = form.address.data
    venue.phone = form.phone.data
    venue.genres = form.genres.data
    venue.image_link = form.image_link.data
    venue.facebook_link = form.facebook_link.data
    venue.website_link = form.website_link.data
    venue.seeking_talent = form.seeking_talent.data
    venue.seeking_description = form.seeking_description.data
    db.session.commit()
  except Exception as e:
    flash(e)
    db.session.rollback()
  finally:
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  try:
  # called upon submitting the new artist listing form
  # DONE: insert form data as a new Venue record in the db, instead
  # DONE: modify data to be the data object returned from db insertion
    form = ArtistForm(request.form)
    artist = Artist()
    form.populate_obj(artist)
    db.session.add(artist)
    db.session.commit()
    # on successful db insert, flash success
    flash('Artist ' + request.form['name'] + ' was successfully created!')
  except:
  # DONE: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Artist ' + request.form['name'] + ' could not be created.')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # DONE: replace with real venues data.
  results = db.session.query(Show, Venue, Artist)\
    .join(Venue, Show.venue_id == Venue.id)\
    .join(Artist, Show.artist_id == Artist.id)\
    .order_by(Show.start_time)\
    .all()

  shows = []
  for show, venue, artist in results:
    shows.append({
        "venue_id": venue.id,
        "venue_name": venue.name,
        "artist_id": artist.id,
        "artist_name": artist.name,
        "artist_image_link": artist.image_link,
        "start_time": str(show.start_time)
    })

  return render_template('pages/shows.html', shows=shows)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  try:
  # called to create new shows in the db, upon submitting new show listing form
  # DONE: insert form data as a new Show record in the db, instead
    form = ShowForm()
    show = Show(
      artist_id = form.artist_id.data,
      venue_id = form.venue_id.data,
      start_time = form.start_time.data
    )
    db.session.add(show)
    db.session.commit()
    # on successful db insert, flash success
    flash('Show was successfully created!')
  except:
  # DONE: on unsuccessful db insert, flash an error instead.
    flash('An error occurred. Show could not be created.')
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
