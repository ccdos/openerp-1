from osv import fields,osv

class student(osv.osv):
    _name = 'student'
    _columns = {
        'name': fields.char('name',size=30,required=True, help='the name'),
        'first_name': fields.char('first name',size=30,required=True, help='the first name'),
        'birth_date': fields.date('birth date',size=30,required=True, help='the birth date'),
        'email': fields.char('email',size=50, help='the email'),
        'phone': fields.integer('phone',size=30, help='the phone'),
        'level': fields.many2one('specialty','Specialty', help='the Specialty'),
    }
student()

class specialty(osv.osv):
    _name = 'specialty'
    _columns = {
        'name': fields.char('Name specialty',size=50,required=True, help='the name specialty'),
        'level': fields.char('Level',size=50, help='the level'),
    }
specialty()