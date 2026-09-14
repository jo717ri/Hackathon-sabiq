import sqlite3

def init_db():
    conn = sqlite3.connect('sabiq.db')
    cursor = conn.cursor()

    # تفعيل مفاتيح الربط الأجنبية في SQLite
    cursor.execute("PRAGMA foreign_keys = ON;")

    try:
        # 1. حذف الجداول القديمة بفرز الترتيب لتفادي تعارض المفاتيح الأجنبية
        cursor.execute("DROP TABLE IF EXISTS TripPassengers")
        cursor.execute("DROP TABLE IF EXISTS Passengers")

        # 2. إنشاء جدول المسافرين (جعل NationalID هو الـ PRIMARY KEY)
        cursor.execute('''
        CREATE TABLE Passengers (
            NationalID TEXT PRIMARY KEY,
            FullName TEXT NOT NULL,
            Relation TEXT NOT NULL,
            PassportStatus TEXT DEFAULT 'Valid',
            HasSecurityRestrictions INTEGER DEFAULT 0, -- 0: سليم, 1: يوجد قيود أمنية
            HasTravelBan INTEGER DEFAULT 0,            -- 0: مسموح له بالسفر, 1: ممنوع من السفر
            UnpaidFines REAL DEFAULT 0
        )
        ''')

        # 3. إنشاء جدول ربط الرحلات والركاب مع المفتاح الأجنبي
        cursor.execute('''
        CREATE TABLE TripPassengers (
            TripID INTEGER PRIMARY KEY AUTOINCREMENT,
            PlateNumber TEXT NOT NULL,
            NationalID TEXT NOT NULL,
            FOREIGN KEY (NationalID) REFERENCES Passengers (NationalID) ON DELETE CASCADE
        )
        ''')

        # 4. إدخال بيانات المسافرين (بدون الحاجة لـ PassengerID)
        passengers_data = [
            ('1011111111', 'خالد عبدالله إبراهيم', 'مالك المركبة', 'Valid', 0, 0, 0),
            ('1022222222', 'هناء ناصر محمد',     'زوجة المالك',  'Valid', 0, 0, 0),
            ('1033333333', 'عبدالله خالد إبراهيم', 'ابن المالك',   'Valid', 0, 0, 0),
            ('1077889900', 'جوري خالد الباز',     'ابنة المالك',  'Valid', 0, 0, 0),
            ('1044444444', 'سعد علي',           'سائق معتمد',  'Valid', 0, 0, 500),
            ('1055555555', 'فهد سالم',          'مرافق',       'Expired', 1, 1, 0)
        ]

        cursor.executemany('''
        INSERT INTO Passengers (NationalID, FullName, Relation, PassportStatus, HasSecurityRestrictions, HasTravelBan, UnpaidFines)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', passengers_data)

        # 5. ربط المسافرين بالمركبات
        trip_data = [
            ('أ ب ج 1234', '1011111111'),
            ('أ ب ج 1234', '1022222222'),
            ('أ ب ج 1234', '1033333333'),
            ('أ ب ج 1234', '1077889900'),
            ('ح خ د 5678', '1044444444'),
            ('ر س ط 9999', '1055555555')
        ]

        cursor.executemany('''
        INSERT INTO TripPassengers (PlateNumber, NationalID)
        VALUES (?, ?)
        ''', trip_data)

        conn.commit()
        print("✅ تم إعادة إنشاء الجداول بنجاح مع اعتماد NationalID كمفتاح رئيسي!")

    except sqlite3.Error as e:
        conn.rollback()
        print(f"❌ حدث خطأ أثناء تهيئة قاعدة البيانات: {e}")

    finally:
        conn.close()

if __name__ == '__main__':
    init_db()