from sqlalchemy import Column, Integer, String, Date
from app.database import Base

class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    nis = Column(Integer, unique=True, index=True)
    nama = Column(String(100))
    jenis_kelamin = Column(String(1))
    tempat_lahir = Column(String(100))
    tanggal_lahir = Column(Date)
    agama = Column(String(50))
    alamat = Column(String(255))
    nama_ortu = Column(String(100))
    no_telp = Column(String(20))
    thn_ajaran = Column(Integer)
    thn_masuk = Column(Integer)
    foto = Column(String(255))
    status = Column(String(50))
    kd_kelas = Column(Integer)
