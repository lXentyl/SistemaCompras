from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta

app = Flask(__name__) 


app.secret_key = 'clave-ultra-secreta-123'
app.permanent_session_lifetime = timedelta(minutes=30)


app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost/sistema'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# MODELO: Departamento
class Departamento(db.Model):
    __tablename__ = 'departamentos'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.Enum('Activo', 'Inactivo'), nullable=False)

# MODELO: Proveedor 
class Proveedor(db.Model):
    __tablename__ = 'proveedores'
    id = db.Column(db.Integer, primary_key=True)
    cedula_rnc = db.Column(db.String(20), nullable=False)
    nombre_comercial = db.Column(db.String(100), nullable=False)
    estado = db.Column(db.Enum('Activo', 'Inactivo'), nullable=False)

def validar_cedula(cedula: str) -> bool:
    cedula = cedula.replace("-", "").strip()

    if len(cedula) != 11 or not cedula.isdigit():
        return False

    verificador = int(cedula[-1])
    multiplicadores = [1, 2] * 5
    suma = 0

    for i in range(10):
        digito = int(cedula[i])
        producto = digito * multiplicadores[i]
        if producto >= 10:
            producto = (producto // 10) + (producto % 10)
        suma += producto

    resultado = (10 - (suma % 10)) % 10
    return resultado == verificador

# MODELO: Unidades de medida
class Unidad(db.Model):
    __tablename__ = 'unidades'
    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(50), nullable=False)
    estado = db.Column(db.Enum('Activo', 'Inactivo'), nullable=False)

# MODELO: Articulos
class Articulo(db.Model):
    __tablename__ = 'articulos'
    id = db.Column(db.Integer, primary_key=True)
    descripcion = db.Column(db.String(100), nullable=False)
    marca = db.Column(db.String(50), nullable=False)
    unidad_id = db.Column(db.Integer, db.ForeignKey('unidades.id'), nullable=False)
    existencia = db.Column(db.Integer, nullable=False)
    estado = db.Column(db.Enum('Activo', 'Inactivo'), nullable=False)

    unidad = db.relationship('Unidad', backref='articulos')



# MODELO: Usuario
class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    usuario = db.Column(db.String(50), nullable=False)
    clave = db.Column(db.String(100), nullable=False)



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

@app.route('/proveedores')
def listar_proveedores():
    proveedores = Proveedor.query.all()
    return render_template('proveedores_list.html', proveedores=proveedores)

@app.route('/proveedores/nuevo', methods=['GET', 'POST'])
def nuevo_proveedor():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        cedula_rnc = request.form['cedula_rnc']
        nombre_comercial = request.form['nombre_comercial']
        estado = request.form['estado']

        # ⛔ Aquí se valida
        if not validar_cedula(cedula_rnc):
            error = "La cédula ingresada no es válida."
            return render_template('proveedores_form.html', proveedor=None, error=error)

        # ✅ Si es válida, guarda
        nuevo = Proveedor(
            cedula_rnc=cedula_rnc,
            nombre_comercial=nombre_comercial,
            estado=estado
        )
        db.session.add(nuevo)
        db.session.commit()
        return redirect(url_for('listar_proveedores'))
    return render_template('proveedores_form.html', proveedor=None)

@app.route('/proveedores/editar/<int:id>', methods=['GET', 'POST'])
def editar_proveedor(id):
    proveedor = Proveedor.query.get_or_404(id)
    if request.method == 'POST':
        proveedor.cedula_rnc = request.form['cedula_rnc']
        proveedor.nombre_comercial = request.form['nombre_comercial']
        proveedor.estado = request.form['estado']
        db.session.commit()
        return redirect(url_for('listar_proveedores'))
    return render_template('proveedores_form.html', proveedor=proveedor)

@app.route('/proveedores/eliminar/<int:id>')
def eliminar_proveedor(id):
    proveedor = Proveedor.query.get_or_404(id)
    db.session.delete(proveedor)
    db.session.commit()
    return redirect(url_for('listar_proveedores'))

@app.route('/unidades')
def listar_unidades():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    unidades = Unidad.query.all()
    return render_template('unidades_list.html', unidades=unidades)

@app.route('/unidades/nuevo', methods=['GET', 'POST'])
def nueva_unidad():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        descripcion = request.form['descripcion']
        estado = request.form['estado']
        nueva = Unidad(descripcion=descripcion, estado=estado)
        db.session.add(nueva)
        db.session.commit()
        return redirect(url_for('listar_unidades'))
    return render_template('unidades_form.html', unidad=None)

@app.route('/unidades/editar/<int:id>', methods=['GET', 'POST'])
def editar_unidad(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    unidad = Unidad.query.get_or_404(id)
    if request.method == 'POST':
        unidad.descripcion = request.form['descripcion']
        unidad.estado = request.form['estado']
        db.session.commit()
        return redirect(url_for('listar_unidades'))
    return render_template('unidades_form.html', unidad=unidad)

@app.route('/unidades/eliminar/<int:id>')
def eliminar_unidad(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    unidad = Unidad.query.get_or_404(id)
    db.session.delete(unidad)
    db.session.commit()
    return redirect(url_for('listar_unidades'))

@app.route('/articulos')
def listar_articulos():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    articulos = Articulo.query.all()
    return render_template('articulos_list.html', articulos=articulos)

@app.route('/articulos/nuevo', methods=['GET', 'POST'])
def nuevo_articulo():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    unidades = Unidad.query.all()
    if request.method == 'POST':
        descripcion = request.form['descripcion']
        marca = request.form['marca']
        unidad_id = request.form['unidad_id']
        existencia = request.form['existencia']
        estado = request.form['estado']

        nuevo = Articulo(
            descripcion=descripcion,
            marca=marca,
            unidad_id=unidad_id,
            existencia=existencia,
            estado=estado
        )
        db.session.add(nuevo)
        db.session.commit()
        return redirect(url_for('listar_articulos'))

    return render_template('articulos_form.html', articulo=None, unidades=unidades)

@app.route('/articulos/editar/<int:id>', methods=['GET', 'POST'])
def editar_articulo(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    articulo = Articulo.query.get_or_404(id)
    unidades = Unidad.query.all()
    if request.method == 'POST':
        articulo.descripcion = request.form['descripcion']
        articulo.marca = request.form['marca']
        articulo.unidad_id = request.form['unidad_id']
        articulo.existencia = request.form['existencia']
        articulo.estado = request.form['estado']
        db.session.commit()
        return redirect(url_for('listar_articulos'))
    return render_template('articulos_form.html', articulo=articulo, unidades=unidades)

@app.route('/articulos/eliminar/<int:id>')
def eliminar_articulo(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    articulo = Articulo.query.get_or_404(id)
    db.session.delete(articulo)
    db.session.commit()
    return redirect(url_for('listar_articulos'))



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        clave = request.form['clave']
        user = Usuario.query.filter_by(usuario=usuario, clave=clave).first()
        if user:
            session['usuario'] = user.usuario
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Usuario o clave incorrectos')
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))



if __name__ == '__main__':
    app.run(debug=True)
