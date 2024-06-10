from pydantic import BaseModel
from datetime import date

class StudentBase(BaseModel):
    nis: int
    nama: str
    jenis_kelamin: str
    tempat_lahir: str
    tanggal_lahir: date
    agama: str
    alamat: str
    nama_ortu: str
    no_telp: str
    thn_ajaran: int
    thn_masuk: int
    foto: str
    status: str
    kd_kelas: int

class StudentCreate(StudentBase):
    pass

class StudentUpdate(StudentBase):
    pass

class Student(StudentBase):
    id: int

    class Config:
        orm_mode = True
