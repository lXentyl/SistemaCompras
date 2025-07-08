from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# Conexión a tu base de datos MySQL desde XAMPP
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/sistema'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# MODELO: Departamento
class Departamento(db.Model):
    __tablename__ = 'departamentos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.Enum('Activo', 'Inactivo'), nullable=False)

# ---------- RUTAS CRUD ----------

@app.route('/')
def index():
    return redirect(url_for('listar_departamentos'))

@app.route('/departamentos')
def listar_departamentos():
    departamentos = Departamento.query.all()
    return render_template('departamentos_list.html', departamentos=departamentos)

@app.route('/departamentos/nuevo', methods=['GET', 'POST'])
def nuevo_departamento():
    if request.method == 'POST':
        nombre = request.form['nombre']
        estado = request.form['estado']
        nuevo = Departamento(nombre=nombre, estado=estado)
        db.session.add(nuevo)
        db.session.commit()
        return redirect(url_for('listar_departamentos'))
    return render_template('departamentos_form.html', departamento=None)

@app.route('/departamentos/editar/<int:id>', methods=['GET', 'POST'])
def editar_departamento(id):
    departamento = Departamento.query.get_or_404(id)
    if request.method == 'POST':
        departamento.nombre = request.form['nombre']
        departamento.estado = request.form['estado']
        db.session.commit()
        return redirect(url_for('listar_departamentos'))
    return render_template('departamentos_form.html', departamento=departamento)

@app.route('/departamentos/eliminar/<int:id>')
def eliminar_departamento(id):
    departamento = Departamento.query.get_or_404(id)
    db.session.delete(departamento)
    db.session.commit()
    return redirect(url_for('listar_departamentos'))

if __name__ == '__main__':
    app.run(debug=True)
