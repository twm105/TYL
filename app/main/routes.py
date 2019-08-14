from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, \
    jsonify, current_app
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from guess_language import guess_language
from app import db
from app.main.forms import EditProfileForm, RecordForm, SearchForm, MessageForm
from app.models import User, Record, Site, Camera
from app.translate import translate
from app.main import bp


@bp.before_app_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
        # g.search_form = SearchForm()
    g.locale = str(get_locale())


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    sites = Site.query.paginate(
        page, current_app.config['ITEMS_PER_PAGE'], False)
    next_url = url_for('main.index', page=sites.next_num) \
        if sites.has_next else None
    prev_url = url_for('main.index', page=sites.prev_num) \
        if sites.has_prev else None
    return render_template('index.html', title=_('Home'),
                           sites=sites.items, next_url=next_url,
                           prev_url=prev_url)


# @bp.route('/explore')
# @login_required
# def explore():
#     page = request.args.get('page', 1, type=int)
#     posts = Post.query.order_by(Post.timestamp.desc()).paginate(
#         page, current_app.config['POSTS_PER_PAGE'], False)
#     next_url = url_for('main.explore', page=posts.next_num) \
#         if posts.has_next else None
#     prev_url = url_for('main.explore', page=posts.prev_num) \
#         if posts.has_prev else None
#     return render_template('index.html', title=_('Explore'),
#                            posts=posts.items, next_url=next_url,
#                            prev_url=prev_url)


@bp.route('/user', methods=['GET', 'POST'])
@login_required
def user():    
    return render_template('user.html', user=current_user)


# TODO secure admin route!
@bp.route('/admin', methods=['GET', 'POST'])
@login_required
def admin():
    if current_user.auth_level != 1:
        flash(_('Permission denied!'))
        return redirect(url_for('main.index'))
    return redirect(url_for('main.admin'))


@bp.route('/site/<site_name>', methods=['GET', 'POST'])
@login_required
def site(site_name):
    form = RecordForm()
    page = request.args.get('page', 1, type=int)
    site=Site.query.filter_by(name=site_name).first_or_404()
    if form.validate_on_submit():
        site.latest_count = form.count.data
        record = Record(site_id=site.id,
                        user_id=current_user.id,
                        count=form.count.data,
                        comments=form.comments.data)
        db.session.add(record)
        db.session.commit()
        flash(_('Record saved'))
        return redirect(url_for('main.site', site_name=site.name))
    cameras = Camera.query.filter_by(site_id=site.id).paginate(
        page, current_app.config['ITEMS_PER_PAGE'], False)
    next_url = url_for('site', page=cameras.next_num) \
        if cameras.has_next else None
    prev_url = url_for('site', page=cameras.prev_num) \
        if cameras.has_prev else None
    return render_template('site.html',
                           title=site.name,
                           site=site,
                           cameras=cameras.items,
                           form=form,
                           prev_url=prev_url,
                           next_url=next_url)


@bp.route('/camera/<camera_name>', methods=['GET', 'POST'])
@login_required
def camera(camera_name):
    camera=Camera.query.filter_by(name=camera_name).first_or_404()
    return render_template('camera.html', title=camera.name, camera=camera)

@bp.route('/translate', methods=['POST']) # TODO revise how translate works
@login_required
def translate_text():
    return jsonify({'text': translate(request.form['text'],
                                      request.form['source_language'],
                                      request.form['dest_language'])})


# @bp.route('/search')
# @login_required
# def search():
#     if not g.search_form.validate():
#         return redirect(url_for('main.explore'))
#     page = request.args.get('page', 1, type=int)
#     posts, total = Post.search(g.search_form.q.data, page,
#                                current_app.config['POSTS_PER_PAGE'])
#     next_url = url_for('main.search', q=g.search_form.q.data, page=page + 1) \
#         if total > page * current_app.config['POSTS_PER_PAGE'] else None
#     prev_url = url_for('main.search', q=g.search_form.q.data, page=page - 1) \
#         if page > 1 else None
#     return render_template('search.html', title=_('Search'), posts=posts,
#                            next_url=next_url, prev_url=prev_url)


# @bp.route('/user/<username>/popup')
# @login_required
# def user_popup(username):
#     user = User.query.filter_by(username=username).first_or_404()
#     return render_template('user_popup.html', user=user)


# @bp.route('/send_message/<recipient>', methods=['GET', 'POST'])
# @login_required
# def send_message(recipient):
#     user = User.query.filter_by(username=recipient).first_or_404()
#     form = MessageForm()
#     if form.validate_on_submit():
#         msg = Message(author=current_user, recipient=user,
#                       body=form.message.data)
#         db.session.add(msg)
#         user.add_notification('unread_message_count', user.new_messages())
#         db.session.commit()
#         flash(_('Your message has been sent.'))
#         return redirect(url_for('main.user', username=recipient))
#     return render_template('send_message.html', title=_('Send Message'),
#                            form=form, recipient=recipient)


# @bp.route('/messages')
# @login_required
# def messages():
#     current_user.last_message_read_time = datetime.utcnow()
#     current_user.add_notification('unread_message_count', 0)
#     db.session.commit()
#     page = request.args.get('page', 1, type=int)
#     messages = current_user.messages_received.order_by(
#         Message.timestamp.desc()).paginate(
#             page, current_app.config['POSTS_PER_PAGE'], False)
#     next_url = url_for('main.messages', page=messages.next_num) \
#         if messages.has_next else None
#     prev_url = url_for('main.messages', page=messages.prev_num) \
#         if messages.has_prev else None
#     return render_template('messages.html', messages=messages.items,
#                            next_url=next_url, prev_url=prev_url)


# @bp.route('/notifications')
# @login_required
# def notifications():
#     since = request.args.get('since', 0.0, type=float)
#     notifications = current_user.notifications.filter(
#         Notification.timestamp > since).order_by(Notification.timestamp.asc())
#     return jsonify([{
#         'name': n.name,
#         'data': n.get_data(),
#         'timestamp': n.timestamp
#     } for n in notifications])