from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_migrate import Migrate
import os
from flask import Flask, render_template
import random

from flask import Flask, render_template, session, request, redirect, url_for



# Инициализация приложения Flask
app = Flask(__name__)

# Настройка базы данных и конфигурации
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'  # Путь к базе данных
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg'}
app.secret_key = 'your_secret_key'  # Убедитесь, что ключ секретный

# Инициализация базы данных и миграций
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Инициализация Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'signin'  # Роут для входа

# Модели базы данных
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150))
    email = db.Column(db.String(150), unique=True)
    password = db.Column(db.String(150))
    favorite_looks = db.relationship('FavoriteLook', backref='user', lazy=True, cascade="all, delete")
    items = db.relationship('WardrobeItem', backref='owner', lazy=True, cascade="all, delete")

class WardrobeItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class FavoriteLook(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    look_name = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

# Загрузка пользователя для Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# Главная страница
@app.route('/')
def home():
    return render_template('home.html')  # Страница Home доступна всем пользователям

# Страница Main (для авторизованных пользователей)
@app.route('/main')
@login_required
def main():
    return render_template('main.html')  # Страница Main доступна только авторизованным пользователям

# Страница профиля
@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        new_name = request.form.get('name')
        new_email = request.form.get('email')
        new_password = request.form.get('password')

        current_user.name = new_name
        current_user.email = new_email

        if new_password:
            current_user.password = generate_password_hash(new_password, method='pbkdf2:sha256')

        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))

    return render_template('profile.html', user=current_user)

# Страница регистрации
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return redirect(url_for('register'))  # Перенаправляем на страницу регистрации

        hashed_password = generate_password_hash(password, method='pbkdf2:sha256')

        if User.query.filter_by(email=email).first():
            flash('A user with this email already exists', 'danger')
            return redirect(url_for('register'))  # Перенаправляем на страницу регистрации

        new_user = User(name=name, email=email, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        flash('Registration successful! You are now logged in.', 'success')

        return redirect(url_for('main'))  # Перенаправляем на главную страницу после успешной регистрации

    return render_template('register.html')  # Страница регистрации

# Страница входа
@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if current_user.is_authenticated:
        return redirect(url_for('main'))  # Если пользователь уже авторизован, перенаправляем на главную страницу

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('main'))  # Перенаправляем на главную страницу после успешного входа

        flash('Invalid credentials', 'danger')

    return render_template('signin.html')  # Страница входа

# Удаление аккаунта
@app.route('/delete-account', methods=['POST'])
@login_required
def delete_account():
    db.session.delete(current_user)
    db.session.commit()

    logout_user()

    flash('Your account has been successfully deleted.', 'success')

    return redirect(url_for('home'))

# Страница загрузки одежды
@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_item():
    if request.method == 'POST':
        name = request.form['name']
        category = request.form['category']
        file = request.files['file']

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            image_url = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            # Создаем новый элемент гардероба для текущего пользователя
            new_item = WardrobeItem(name=name, category=category, image_url=image_url, user_id=current_user.id)
            db.session.add(new_item)
            db.session.commit()

            flash('Item uploaded successfully!', 'success')
            return redirect(url_for('wardrobe'))

    return render_template('upload_item.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

# Страница гардероба
@app.route('/wardrobe', methods=['GET'])
@login_required
def wardrobe():
    category = request.args.get('category')  # Получаем параметр category из URL
    if category and category != 'all':  # Если категория есть в URL и она не 'all'
        items = WardrobeItem.query.filter_by(user_id=current_user.id, category=category).all()
    else:  # Если категории нет (или 'all')
        items = WardrobeItem.query.filter_by(user_id=current_user.id).all()  # Показываем все элементы
    return render_template('wardrobe.html', items=items)


# Удаление предмета из гардероба
@app.route('/delete_item/<int:item_id>', methods=['POST'])
@login_required
def delete_item(item_id):
    item = WardrobeItem.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    flash('Item deleted successfully!', 'success')
    return redirect(url_for('wardrobe'))

# Функция для отображения загруженных файлов
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Страница избранных образов
@app.route('/favorites_look')
@login_required
def favorites_look():
    favorites = current_user.favorite_looks if current_user.favorite_looks else None
    if not favorites:
        return render_template('favorite_looks.html')  # Если нет избранных образов
    return render_template('favorite_looks.html', favorites=favorites)  # Отображаем избранные образы

@app.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()  # Выход пользователя
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))  # Перенаправляем на главную страницу после выхода

@app.route('/reset-password', methods=['GET', 'POST'])
def reset_password():
    if request.method == 'POST':
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']
        email = request.form.get('email')

        if not email:
            return "Email is required", 400

        if new_password != confirm_password:
            return "Passwords do not match", 400

        hashed_password = generate_password_hash(new_password)
        user = User.query.filter_by(email=email).first()
        if user:
            user.password = hashed_password
            db.session.commit()
            flash('Password reset successfully.', 'success')
            return redirect(url_for('signin'))

        flash('Email not found.', 'danger')

    return render_template('reset-password.html')

@app.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        new_name = request.form.get('name')
        new_email = request.form.get('email')

        # Обновляем данные пользователя в базе данных
        current_user.name = new_name
        current_user.email = new_email
        db.session.commit()

        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile'))  # Перенаправляем обратно на профиль

    return render_template('edit-profile.html', user=current_user)
    







# Пример списка изображений по категориям
items = {
    'Tops': ['top1.png', 'top2.png', 'top3.png'],
    'Bottoms': ['bottom1.png', 'bottom2.png', 'bottom3.png'],
    'Shoes': ['shoes1.png', 'shoes2.png', 'shoes3.png'],
    'Accessories': ['accessory1.png', 'accessory2.png', 'accessory3.png'],
    'Outerwear': ['outerwear1.png', 'outerwear2.png', 'outerwear3.png']
}

@app.route('/generate_outfit', methods=['GET', 'POST'])
def generate_outfit():
    # Генерация случайных изображений для каждого типа одежды
    top_image = random.choice(items['Tops'])
    bottom_image = random.choice(items['Bottoms'])
    shoes_image = random.choice(items['Shoes'])
    accessories_image = random.choice(items['Accessories'])
    outerwear_image = random.choice(items['Outerwear'])

    # Отправка данных в HTML-шаблон
    if request.method == 'POST':
        outfit_name = request.form.get('lookName')
        if outfit_name:
            # Сохраняем аутфит в сессию, если нажали кнопку "Save to Favorite Looks"
            if 'favorite_looks' not in session:
                session['favorite_looks'] = []
            session['favorite_looks'].append({
                'name': outfit_name,
                'top_image': top_image,
                'bottom_image': bottom_image,
                'shoes_image': shoes_image,
                'accessories_image': accessories_image,
                'outerwear_image': outerwear_image
            })
            session.modified = True  # Обновляем сессию
            return redirect(url_for('favorite_looks'))

    return render_template('generate_outfit.html', 
                           top_image=top_image,
                           bottom_image=bottom_image,
                           shoes_image=shoes_image,
                           accessories_image=accessories_image,
                           outerwear_image=outerwear_image)


@app.route('/favorite_looks')
def favorite_looks():
    # Получаем сохраненные аутфиты из сессии
    favorite_looks = session.get('favorite_looks', [])
    return render_template('favorite_looks.html', favorite_looks=favorite_looks)

@app.route('/view_outfit/<int:outfit_id>')
def view_outfit(outfit_id):
    # Получаем конкретный аутфит по id
    favorite_looks = session.get('favorite_looks', [])
    if outfit_id < len(favorite_looks):
        outfit = favorite_looks[outfit_id]
        return render_template('view_outfit.html', outfit=outfit)
    return redirect(url_for('favorite_looks'))



if __name__ == '__main__':
    app.run(debug=True)
