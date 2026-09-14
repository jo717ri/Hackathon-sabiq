from flask import Flask, render_template_string, jsonify, request
import sqlite3
import datetime
import uuid
DB_NAME = 'sabiq.db'
def get_db_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn
ENTERPRISE_HTML = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>منظومة سَابِق - مركز التحكم والعبور الذكي</title>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {
            --bg-main: #0b0f19;
            --panel-bg: #111827;
            --panel-border: #1f293d;
            --accent-blue: #0284c7;
            --accent-green: #10b981;
            --accent-yellow: #f59e0b;
            --accent-red: #ef4444;
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
        }
        * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; }
        body { background-color: var(--bg-main); color: var(--text-main); min-height: 100vh; padding: 15px; }
        header { display: flex; justify-content: space-between; align-items: center; background: var(--panel-bg); padding: 15px 25px; border-radius: 12px; border: 1px solid var(--panel-border); margin-bottom: 20px; }
        .logo-area { display: flex; align-items: center; gap: 15px; }
        .logo-area i { font-size: 28px; color: var(--accent-blue); }
        .logo-area h1 { font-size: 20px; font-weight: 700; letter-spacing: -0.5px; }
        .system-badge { background: rgba(2, 132, 199, 0.15); color: #38bdf8; padding: 4px 12px; border-radius: 20px; font-size: 12px; border: 1px solid rgba(56, 189, 248, 0.3); }
        .live-status { display: flex; align-items: center; gap: 20px; font-size: 14px; }
        .status-indicator { display: flex; align-items: center; gap: 8px; }
        .dot { width: 10px; height: 10px; background: var(--accent-green); border-radius: 50%; box-shadow: 0 0 8px var(--accent-green); animation: pulse 2s infinite; }
        @keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }
        .stats-grid { display: grid; grid-template-columns: repeat(5, 1fr); gap: 15px; margin-bottom: 20px; }
        .stat-card { background: var(--panel-bg); border: 1px solid var(--panel-border); border-radius: 10px; padding: 15px; display: flex; align-items: center; justify-content: space-between; }
        .stat-value { font-size: 22px; font-weight: bold; margin-top: 5px; transition: all 0.3s ease; }
        .stat-icon { font-size: 24px; opacity: 0.8; }
        .dashboard-grid { display: grid; grid-template-columns: 1fr 1.8fr; gap: 20px; }
        .panel { background: var(--panel-bg); border: 1px solid var(--panel-border); border-radius: 12px; padding: 20px; }
        .panel-header { font-size: 16px; font-weight: 600; margin-bottom: 15px; display: flex; align-items: center; gap: 10px; color: var(--text-muted); }
        .camera-feed { width: 100%; height: 210px; background: #000; border-radius: 8px; margin-bottom: 20px; position: relative; border: 1px solid #374151; overflow: hidden; display: flex; align-items: center; justify-content: center; }
        .camera-overlay { position: absolute; top: 10px; right: 10px; background: rgba(0,0,0,0.6); padding: 4px 8px; border-radius: 4px; font-size: 11px; color: #ef4444; }
        .scanner-line { position: absolute; width: 100%; height: 2px; background: rgba(56, 189, 248, 0.8); box-shadow: 0 0 10px #38bdf8; top: 0; animation: scan 3s infinite linear; }
        @keyframes scan { 0% { top: 0%; } 50% { top: 100%; } 100% { top: 0%; } }
        .search-form { display: flex; gap: 10px; }
        .search-form input { flex: 1; background: #0b0f19; border: 1px solid var(--panel-border); padding: 12px 15px; border-radius: 8px; color: white; font-size: 16px; text-align: center; font-weight: bold; }
        .search-form input:focus { outline: none; border-color: var(--accent-blue); }
        .search-form button { background: var(--accent-blue); color: white; border: none; padding: 0 25px; border-radius: 8px; font-weight: bold; cursor: pointer; transition: 0.2s; }
        .search-form button:hover { background: #0369a1; }
        .decision-box { border-radius: 10px; padding: 25px; border: 1px solid transparent; display: none; height: 100%; flex-direction: column; justify-content: space-between; }
        .decision-box.GREEN { background: rgba(16, 185, 129, 0.08); border-color: rgba(16, 185, 129, 0.4); }
        .decision-box.YELLOW { background: rgba(245, 158, 11, 0.08); border-color: rgba(245, 158, 11, 0.4); }
        .decision-box.RED { background: rgba(239, 68, 68, 0.08); border-color: rgba(239, 68, 68, 0.4); }
        .decision-header { display: flex; align-items: center; gap: 15px; margin-bottom: 15px; }
        .decision-icon { font-size: 36px; }
        .GREEN .decision-icon { color: var(--accent-green); }
        .YELLOW .decision-icon { color: var(--accent-yellow); }
        .RED .decision-icon { color: var(--accent-red); }
        .token-badge { display: inline-block; background: #1e293b; border: 1px dashed #475569; padding: 8px 16px; border-radius: 6px; font-family: monospace; font-size: 16px; font-weight: bold; margin-top: 10px; color: #38bdf8; }
        .passengers-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(230px, 1fr)); gap: 12px; margin-top: 20px; }
        .passenger-card { background: rgba(17, 24, 39, 0.9); border: 1px solid var(--panel-border); padding: 12px; border-radius: 10px; display: flex; align-items: center; gap: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        .passenger-avatar { width: 44px; height: 44px; border-radius: 50%; background: #1e293b; border: 2px solid var(--accent-blue); display: flex; align-items: center; justify-content: center; color: #94a3b8; font-size: 20px; flex-shrink: 0; }
        .passenger-info { flex: 1; display: flex; flex-direction: column; gap: 2px; }
        .passenger-info .name { font-weight: 600; font-size: 13px; color: #f3f4f6; }
        .passenger-info .meta { font-size: 11px; color: var(--text-muted); display: flex; justify-content: space-between; align-items: center; margin-top: 2px; }
        .btn-add-passenger { background: #1e293b; border: 1px solid var(--accent-blue); color: #38bdf8; padding: 8px 16px; border-radius: 8px; font-size: 13px; font-weight: 600; cursor: pointer; display: flex; align-items: center; gap: 8px; transition: 0.2s; }
        .btn-add-passenger:hover { background: var(--accent-blue); color: #fff; }
        .modal-overlay { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.75); display: none; justify-content: center; align-items: center; z-index: 1000; backdrop-filter: blur(4px); }
        .modal-card { background: var(--panel-bg); border: 1px solid var(--panel-border); border-radius: 14px; width: 430px; padding: 25px; text-align: center; box-shadow: 0 10px 25px rgba(0,0,0,0.5); }
        .fingerprint-icon { font-size: 65px; color: var(--accent-blue); margin: 15px 0; cursor: pointer; transition: all 0.3s ease; }
        .fingerprint-icon:hover { transform: scale(1.08); color: var(--accent-green); }
        .table-panel { margin-top: 20px; }
        table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 14px; }
        th, td { text-align: right; padding: 12px; border-bottom: 1px solid var(--panel-border); }
        th { color: var(--text-muted); font-weight: 500; }
        .badge { padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 500; display: inline-block; }
        .badge-green { background: rgba(16, 185, 129, 0.2); color: #34d399; }
        .badge-yellow { background: rgba(245, 158, 11, 0.2); color: #fbbf24; }
        .badge-red { background: rgba(239, 68, 68, 0.2); color: #f87171; }
    </style>
</head>
<body>
    <header>
        <div class="logo-area">
            <i class="fa-solid fa-shield-halved"></i>
            <div>
                <h1>منظومة "سَابِق" للعبور الذكي</h1>
                <span style="font-size: 12px; color: var(--text-muted);">منفذ الجوازات والجمارك | الكابينة رقم #04</span>
            </div>
            <span class="system-badge">نسخة الهاكاثون </span>
        </div>
        <div class="live-status">
            <div class="status-indicator">
                <div class="dot"></div>
                <span>الكاميرات وأنظمة AI متصلة</span>
            </div>
            <span style="color: var(--panel-border);">|</span>
            <div id="clock" style="font-family: monospace; font-size: 15px;"></div>
        </div>
    </header>

    <div class="stats-grid">
        <div class="stat-card">
            <div>
                <div style="font-size: 11px; color: var(--text-muted);">إجمالي المركبات</div>
                <div class="stat-value" id="statTotal">0</div>
            </div>
            <i class="fa-solid fa-car stat-icon" style="color: var(--accent-blue);"></i>
        </div>
        <div class="stat-card">
            <div>
                <div style="font-size: 11px; color: var(--text-muted);">المسافرون المعبرون (أخضر)</div>
                <div class="stat-value" style="color: #38bdf8;" id="statPassengers">0</div>
            </div>
            <i class="fa-solid fa-users stat-icon" style="color: #38bdf8;"></i>
        </div>
        <div class="stat-card">
            <div>
                <div style="font-size: 11px; color: var(--text-muted);">المسار الأخضر</div>
                <div class="stat-value" style="color: var(--accent-green);" id="statGreen">0</div>
            </div>
            <i class="fa-solid fa-circle-check stat-icon" style="color: var(--accent-green);"></i>
        </div>
        <div class="stat-card">
            <div>
                <div style="font-size: 11px; color: var(--text-muted);">مسار التدقيق</div>
                <div class="stat-value" style="color: var(--accent-yellow);" id="statYellow">0</div>
            </div>
            <i class="fa-solid fa-triangle-exclamation stat-icon" style="color: var(--accent-yellow);"></i>
        </div>
        <div class="stat-card">
            <div>
                <div style="font-size: 11px; color: var(--text-muted);">مسار التحويل</div>
                <div class="stat-value" style="color: var(--accent-red);" id="statRed">0</div>
            </div>
            <i class="fa-solid fa-shield-cat stat-icon" style="color: var(--accent-red);"></i>
        </div>
    </div>

    <div class="dashboard-grid">
        <div class="panel">
            <div class="panel-header">
                <i class="fa-solid fa-camera"></i>
                <span>كاميرا القراءة الآلية (ANPR / OCR)</span>
            </div>
            <div class="camera-feed">
                <div class="camera-overlay"><i class="fa-solid fa-circle"></i> مباشر</div>
                <div class="scanner-line"></div>
                <div style="text-align: center; color: var(--text-muted);">
                    <i class="fa-solid fa-expand" style="font-size: 40px; margin-bottom: 10px; opacity: 0.3;"></i>
                    <p style="font-size: 13px;">في انتظار اقتراب المركبة من الكابينة...</p>
                </div>
            </div>
            <div class="panel-header" style="margin-top: 10px;">
                <i class="fa-solid fa-keyboard"></i>
                <span>فحص اللوحة يدوياً / آلياً</span>
            </div>
            <div class="search-form">
                <input type="text" id="plateInput" placeholder="مثال: أ ب ج 1234">
                <button onclick="checkVehicle()"><i class="fa-solid fa-magnifying-glass"></i> فحص</button>
            </div>
            <p style="font-size: 11px; color: var(--text-muted); margin-top: 8px; text-align: center;">
                جربي اللوحات التجريبية: <strong>أ ب ج 1234</strong> (أخضر) | <strong>د هـ و 7711</strong> (أصفر) | <strong>ر س ط 9999</strong> (أحمر)
            </p>
        </div>

        <div class="panel" style="display: flex; flex-direction: column;">
            <div class="panel-header">
                <i class="fa-solid fa-sliders"></i>
                <span>نتيجة التحقق والقرار الآلي (AI Decision Engine)</span>
            </div>
            <div id="placeholderView" style="text-align: center; padding: 60px 20px; color: var(--text-muted);">
                <i class="fa-solid fa-id-card-clip" style="font-size: 50px; margin-bottom: 15px; opacity: 0.2;"></i>
                <p>أدخلي رقم اللوحة أو انتظري قراءة الكاميرا لعرض نتائج التحقق والأدوار الأمنية.</p>
            </div>
            <div id="decisionCard" class="decision-box">
                <div>
                    <div class="decision-header">
                        <i id="decisionIcon" class="fa-solid decision-icon"></i>
                        <div>
                            <h2 id="decisionTitle" style="font-size: 20px;"></h2>
                            <p id="decisionDesc" style="font-size: 13px; color: var(--text-muted); margin-top: 4px;"></p>
                        </div>
                    </div>
                    <div style="margin-top: 15px;">
                        <span style="font-size: 12px; color: var(--text-muted);">رمز تصريح العبور المؤقت (Encrypted Pass Token):</span><br>
                        <div id="tokenText" class="token-badge"></div>
                    </div>
                    <div style="margin-top: 20px;">
                        <div style="font-size: 13px; font-weight: 600; color: var(--text-muted); margin-bottom: 10px;">
                            <i class="fa-solid fa-users"></i> الركاب المسجلين وتطابق الوجوه (Biometric Verification):
                        </div>
                        <div id="passengersGrid" class="passengers-grid"></div>
                    </div>
                </div>
                <div style="margin-top: 20px; padding-top: 15px; border-top: 1px solid rgba(255,255,255,0.1); display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 12px; color: var(--text-muted);" id="checkTimeText"></span>
                    <button class="btn-add-passenger" onclick="openBioModal()">
                        <i class="fa-solid fa-fingerprint"></i> قراءة البصمة الحيوية للراكب
                    </button>
                </div>
            </div>
        </div>
    </div>

    <!-- نافذة قراءة البصمة الحيوية -->
    <div id="bioModal" class="modal-overlay">
        <div class="modal-card">
            <h3 style="font-size: 18px; margin-bottom: 4px;">جهاز التحقق بالبصمة الحيوية</h3>
            <p style="font-size: 12px; color: var(--text-muted); margin-bottom: 15px;">اطلبي من الراكب وضع إبهامه على القارئ للمطابقة الآلية</p>
            
            <div style="margin: 10px 0;">
                <i id="bioIcon" class="fa-solid fa-fingerprint fingerprint-icon" onclick="scanBiometricAutomated()"></i>
            </div>

            <div id="bioScanStatus" style="font-size: 13px; color: var(--text-muted); margin-bottom: 15px; min-height: 40px; display: flex; align-items: center; justify-content: center;">
                اضغطي على البصمة أو زر الفحص للبدء...
            </div>

            <!-- معلومات الشخص المسترجعة آلياً -->
            <div id="passengerResultPreview" style="display: none; background: rgba(16, 185, 129, 0.08); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 8px; padding: 12px; margin-bottom: 15px; text-align: right;">
                <div style="font-size: 11px; color: var(--accent-green); font-weight: bold; margin-bottom: 4px;"><i class="fa-solid fa-circle-check"></i> السجل سليم - جاهز للعبور</div>
                <div id="scannedName" style="font-size: 14px; font-weight: bold; color: #fff;">الاسم: سلطان أحمد</div>
                <div id="scannedId" style="font-size: 12px; color: var(--text-muted);">رقم الهوية: 1099887766</div>
            </div>

            <div style="display: flex; gap: 10px; justify-content: center;">
                <button id="btnScanAction" onclick="scanBiometricAutomated()" style="background: var(--accent-blue); border: none; color: white; padding: 10px 18px; border-radius: 6px; cursor: pointer; font-weight: 600; flex: 1;">
                    <i class="fa-solid fa-barcode"></i> مسح البصمة الآن
                </button>
                <button id="btnConfirmPassenger" onclick="confirmAddPassenger()" style="display: none; background: var(--accent-green); border: none; color: white; padding: 10px 18px; border-radius: 6px; cursor: pointer; font-weight: 600; flex: 1.2;">
                    <i class="fa-solid fa-user-check"></i> إضافة وتأكيد العبور
                </button>
                <button onclick="closeBioModal()" style="background: transparent; border: 1px solid var(--panel-border); color: var(--text-muted); padding: 10px 15px; border-radius: 6px; cursor: pointer;">
                    إلغاء
                </button>
            </div>
        </div>
    </div>

    <div class="panel table-panel">
        <div class="panel-header">
            <i class="fa-solid fa-list-check"></i>
            <span>سجل الحركة اللحظي للمنفذ (Live Traffic Activity)</span>
        </div>
        <table>
            <thead>
                <tr>
                    <th>الوقت</th>
                    <th>رقم اللوحة</th>
                    <th>حالة القرار</th>
                    <th>عدد الركاب</th>
                    <th>رمز العبور (Token)</th>
                    <th>المسار الموجه</th>
                </tr>
            </thead>
            <tbody id="trafficLogTable"></tbody>
        </table>
    </div>

    <script>
        let stats = { total: 0, passengers: 0, green: 0, yellow: 0, red: 0 };
        let currentPlate = '';
        let currentStatusCode = '';
        let currentPassengerCount = 0;
        let lastScannedPassenger = { name: '', id: '' };

        setInterval(() => {
            const now = new Date();
            document.getElementById('clock').innerText = now.toLocaleTimeString('ar-SA');
        }, 1000);

        function updateStatsUI() {
            document.getElementById('statTotal').innerText = stats.total.toLocaleString('ar-SA');
            document.getElementById('statPassengers').innerText = stats.passengers.toLocaleString('ar-SA');
            document.getElementById('statGreen').innerText = stats.green.toLocaleString('ar-SA');
            document.getElementById('statYellow').innerText = stats.yellow.toLocaleString('ar-SA');
            document.getElementById('statRed').innerText = stats.red.toLocaleString('ar-SA');
        }

        async function checkVehicle() {
            const plate = document.getElementById('plateInput').value.trim();
            if(!plate) return alert('يرجى إدخال رقم اللوحة');
            currentPlate = plate;

            try {
                const res = await fetch('/api/verify', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({plate_number: plate})
                });
                const data = await res.json();

                stats.total += 1;
                currentStatusCode = data.status_code;

                if (data.status_code === 'GREEN') {
                    stats.green += 1;
                    stats.passengers += data.passengers.length;
                } else if (data.status_code === 'YELLOW') {
                    stats.yellow += 1;
                } else if (data.status_code === 'RED') {
                    stats.red += 1;
                }
                updateStatsUI();

                document.getElementById('placeholderView').style.display = 'none';
                const card = document.getElementById('decisionCard');
                card.className = 'decision-box ' + data.status_code;
                card.style.display = 'flex';

                document.getElementById('decisionTitle').innerText = data.status_title;
                document.getElementById('decisionDesc').innerText = data.status_desc;
                document.getElementById('tokenText').innerText = data.token;
                document.getElementById('checkTimeText').innerText = 'وقت الفحص: ' + data.timestamp;

                const icon = document.getElementById('decisionIcon');
                if(data.status_code === 'GREEN') icon.className = 'fa-solid fa-circle-check decision-icon';
                else if(data.status_code === 'YELLOW') icon.className = 'fa-solid fa-triangle-exclamation decision-icon';
                else icon.className = 'fa-solid fa-circle-xmark decision-icon';

                const grid = document.getElementById('passengersGrid');
                grid.innerHTML = '';
                currentPassengerCount = data.passengers.length;
                
                if(data.passengers.length === 0) {
                    grid.innerHTML = '<p id="emptyPassengersMsg" style="font-size: 12px; color: var(--text-muted);">لا يوجد ركاب مسجلين مسبقاً على هذه اللوحة.</p>';
                } else {
                    data.passengers.forEach(p => {
                        renderPassengerCard(p.name, p.national_id, p.match_rate, false);
                    });
                }
                updateTrafficTable(data.timestamp, plate, data.status_title, data.status_code, currentPassengerCount, data.token);
            } catch(e) {
                alert('تعذر الاتصال بالخادم، يرجى التأكد من تشغيل سكريبت Flask.');
            }
        }

        function renderPassengerCard(name, nationalId, matchRate, isExtra = false) {
            const grid = document.getElementById('passengersGrid');
            const emptyMsg = document.getElementById('emptyPassengersMsg');
            if(emptyMsg) emptyMsg.remove();

            let displayName = isExtra ? `${name} <span style="font-size:10px; color:var(--accent-blue); background:rgba(2,132,199,0.15); padding:2px 6px; border-radius:4px; font-weight:normal;">تأكيد بصمة</span>` : name;
            const cardHtml = `
                <div class="passenger-card">
                    <div class="passenger-avatar"><i class="fa-solid fa-user-tie"></i></div>
                    <div class="passenger-info">
                        <div class="name">${displayName}</div>
                        <div class="meta">
                            <span>هوية: ${nationalId}</span>
                            <span style="color: var(--accent-green); font-weight: 600;"><i class="fa-solid fa-fingerprint"></i> ${matchRate}</span>
                        </div>
                    </div>
                </div>
            `;
            grid.innerHTML += cardHtml;
        }

        function openBioModal() {
            if(!currentPlate) return alert('الرجاء فحص مركبة أولاً قبل قراءة البصمة.');
            
            document.getElementById('bioScanStatus').innerHTML = 'ضع إبهام الراكب على الجهاز واضغط قراءة...';
            document.getElementById('passengerResultPreview').style.display = 'none';
            document.getElementById('btnConfirmPassenger').style.display = 'none';
            document.getElementById('btnScanAction').style.display = 'inline-block';
            document.getElementById('bioIcon').style.color = 'var(--accent-blue)';
            
            document.getElementById('bioModal').style.display = 'flex';
        }

        function closeBioModal() {
            document.getElementById('bioModal').style.display = 'none';
        }

        function scanBiometricAutomated() {
            const statusDiv = document.getElementById('bioScanStatus');
            const icon = document.getElementById('bioIcon');
            
            icon.style.color = 'var(--accent-yellow)';
            statusDiv.innerHTML = '<span style="color: var(--accent-yellow);"><i class="fa-solid fa-spinner fa-spin"></i> جاري مطابقة البصمة البيومترية مع مركز المعلومات الوطني...</span>';
            
            setTimeout(() => {
                lastScannedPassenger = {
                    name: "سلطان أحمد ",
                    id: "1098" + Math.floor(100000 + Math.random() * 900000)
                };

                icon.style.color = 'var(--accent-green)';
                statusDiv.innerHTML = '<span style="color: var(--accent-green); font-weight: bold;"><i class="fa-solid fa-circle-check"></i> تم التعرف على البصمة والسجل سليم!</span>';
                
                document.getElementById('scannedName').innerText = "الاسم: " + lastScannedPassenger.name;
                document.getElementById('scannedId').innerText = "رقم الهوية: " + lastScannedPassenger.id;
                
                document.getElementById('passengerResultPreview').style.display = 'block';
                document.getElementById('btnScanAction').style.display = 'none';
                document.getElementById('btnConfirmPassenger').style.display = 'inline-block';
            }, 1200);
        }

        function confirmAddPassenger() {
            renderPassengerCard(lastScannedPassenger.name, lastScannedPassenger.id, "99.8%", true);
            currentPassengerCount++;

            if (currentStatusCode === 'GREEN') {
                stats.passengers += 1;
                updateStatsUI();
            }
            closeBioModal();

            const firstRow = document.querySelector('#trafficLogTable tr');
            if(firstRow) {
                firstRow.cells[3].innerText = currentPassengerCount + " ركاب";
            }
        }

        function updateTrafficTable(timestamp, plate, statusTitle, statusCode, count, token) {
            const table = document.getElementById('trafficLogTable');
            let badgeClass = statusCode === 'GREEN' ? 'badge-green' : (statusCode === 'YELLOW' ? 'badge-yellow' : 'badge-red');
let laneText = statusCode === 'GREEN' ? 'المسار الأخضر - عبور سريع' : (statusCode === 'YELLOW' ? 'مسار التدقيق والتحقق' : 'المسار الأحمر - تفتيش أمني');            
            const newRow = `
                <tr>
                    <td>${timestamp}</td>
                    <td><strong>${plate}</strong></td>
                    <td><span class="badge ${badgeClass}">${statusTitle}</span></td>
                    <td>${count} ركاب</td>
                    <td>${token}</td>
                    <td>${laneText}</td>
                </tr>
            `;
            table.innerHTML = newRow + table.innerHTML;
        }
        
        updateStatsUI();
    </script>
</body>
</html>
"""

app = Flask(__name__)

@app.route('/')
def index():
    return render_template_string(ENTERPRISE_HTML)

@app.route('/welcome-demo')
def welcome_demo():
    portal_html = """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>منظومة سَابِق - بوابة الدخول الذكية</title>
        <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap" rel="stylesheet">
        <style>body { font-family: 'Cairo', sans-serif; }</style>
    </head>
    <body class="bg-[#0b0f19] text-slate-100 min-h-screen flex flex-col items-center justify-center p-6 relative overflow-hidden">
        <div class="absolute -top-32 -right-32 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl pointer-events-none"></div>
        <div class="absolute -bottom-32 -left-32 w-96 h-96 bg-emerald-600/10 rounded-full blur-3xl pointer-events-none"></div>

        <div class="max-w-3xl w-full text-center z-10">
            <div class="inline-flex items-center justify-center w-20 h-20 bg-blue-600/20 text-blue-400 rounded-2xl mb-6 border border-blue-500/30 shadow-xl shadow-blue-900/20">
                <i class="fa-solid fa-shield-halved text-4xl"></i>
            </div>
            <span class="bg-blue-500/10 text-blue-400 text-xs font-semibold px-3 py-1.5 rounded-full border border-blue-500/20 tracking-wider">
                منظومة العبور الذكي 
            </span>
            <h1 class="text-4xl font-black mt-4 mb-3 tracking-tight">مشروع سَابِق</h1>
            <p class="text-slate-400 text-base max-w-lg mx-auto mb-10">
                نظام رقمي متكامل لتسريع وتأمين حركة العبور عبر المنافذ الحدودية باستخدام تقنيات الذكاء الاصطناعي والمطابقة الحيوية.
            </p>

            <div class="grid md:grid-cols-2 gap-6 text-right">
                <div onclick="location.href='/'" class="group bg-[#111827] border border-[#1f293d] hover:border-blue-500/50 p-6 rounded-2xl cursor-pointer transition-all duration-300 hover:shadow-2xl hover:shadow-blue-500/10 hover:-translate-y-1">
                    <div class="flex items-center justify-between mb-4">
                        <div class="w-12 h-12 rounded-xl bg-blue-500/10 text-blue-400 flex items-center justify-center text-xl group-hover:bg-blue-500 group-hover:text-white transition-colors">
                            <i class="fa-solid fa-desktop"></i>
                        </div>
                        <span class="text-xs text-slate-500 bg-slate-800 px-2.5 py-1 rounded-md">صلاحيات أمنية</span>
                    </div>
                    <h2 class="text-xl font-bold mb-1 group-hover:text-blue-400 transition-colors">لوحة تحكم الموظف</h2>
                    <p class="text-slate-400 text-xs leading-relaxed">
                        إدارة الكابينة، فحص اللوحات آلياً (ANPR)، اتخاذ القرار الاستباقي، ومطابقة البصمات الحيوية.
                    </p>
                </div>

                <div onclick="location.href='/passenger'" class="group bg-[#111827] border border-[#1f293d] hover:border-emerald-500/50 p-6 rounded-2xl cursor-pointer transition-all duration-300 hover:shadow-2xl hover:shadow-emerald-500/10 hover:-translate-y-1">
                    <div class="flex items-center justify-between mb-4">
                        <div class="w-12 h-12 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center text-xl group-hover:bg-emerald-500 group-hover:text-white transition-colors">
                            <i class="fa-solid fa-user-check"></i>
                        </div>
                        <span class="text-xs text-slate-500 bg-slate-800 px-2.5 py-1 rounded-md">خدمات ذاتية</span>
                    </div>
                    <h2 class="text-xl font-bold mb-1 group-hover:text-emerald-400 transition-colors">بوابة المسافر الذكية</h2>
                    <p class="text-slate-400 text-xs leading-relaxed">
                        التحقق المسبق من حالة التصاريح، صلاحية الجوازات، اختيار التابعين، وتحديد المنفذ الحدودي.
                    </p>
                </div>
            </div>

            <div class="mt-12 text-xs text-slate-500">
                جميع الحقوق محفوظة &bull; منظومة سَابِق للعبور الذكي
            </div>
        </div>
    </body>
    </html>
    """
    return render_template_string(portal_html)

@app.route('/passenger')
def passenger_view():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 1. جلب بيانات مالك المركبة الأساسي
    owner_query = '''
        SELECT p.NationalID, p.FullName, p.Relation, p.PassportStatus, 
               p.HasSecurityRestrictions, p.HasTravelBan, p.UnpaidFines
        FROM Passengers p
        JOIN TripPassengers tp ON p.NationalID = tp.NationalID
        WHERE tp.PlateNumber = 'أ ب ج 1234' AND (p.Relation LIKE '%مالك%' OR p.Relation LIKE '%سائق%')
    '''
    cursor.execute(owner_query)
    owner_row = cursor.fetchone()
    
    if not owner_row:
        fallback_query = '''
            SELECT p.NationalID, p.FullName, p.Relation, p.PassportStatus, 
                   p.HasSecurityRestrictions, p.HasTravelBan, p.UnpaidFines
        FROM Passengers p
        JOIN TripPassengers tp ON p.NationalID = tp.NationalID
        WHERE tp.PlateNumber = 'أ ب ج 1234' LIMIT 1
        '''
        cursor.execute(fallback_query)
        owner_row = cursor.fetchone()

    # 2. جلب بقية ركاب العائلة / التابعين لنفس المركبة
    passengers_query = '''
        SELECT p.NationalID, p.FullName, p.Relation, p.PassportStatus, 
               p.HasSecurityRestrictions, p.HasTravelBan, p.UnpaidFines
        FROM Passengers p
        JOIN TripPassengers tp ON p.NationalID = tp.NationalID
        WHERE tp.PlateNumber = 'أ ب ج 1234' AND p.NationalID != ?
    '''
    cursor.execute(passengers_query, (owner_row['NationalID'] if owner_row else '',))
    rows = cursor.fetchall()
    conn.close()

    owner_name = owner_row['FullName'] if owner_row else "غير معروف"
    owner_id = owner_row['NationalID'] if owner_row else "----------"

    passengers_html_items = ""
    for row in rows:
        can_travel = True
        status_text = "حالة السفر: مسموح بالعبور"
        status_class = "text-emerald-400 bg-emerald-500/10 border-emerald-500/30"
        
        if row['HasTravelBan'] == 1 or row['HasSecurityRestrictions'] == 1:
            can_travel = False
            status_text = "ممنوع من السفر (توجد قيود أمنية/منع)"
            status_class = "text-red-400 bg-red-500/10 border-red-500/30"
        elif row['PassportStatus'] != 'Valid' or row['UnpaidFines'] > 0:
            can_travel = False
            status_text = "تعذر السفر (يتطلب تحديث جواز أو سداد مخالفات)"
            status_class = "text-yellow-400 bg-yellow-500/10 border-yellow-500/30"

        passengers_html_items += f"""
            <div class="p-3 bg-[#0b0f19] rounded-xl border border-[#1f293d] flex items-center justify-between">
                <div>
                    <div class="flex items-center gap-2">
                        <span class="text-sm font-bold text-slate-200">{row['FullName']}</span>
                        <span class="text-xs bg-slate-800 text-slate-300 px-2 py-0.5 rounded-md">({row['Relation']})</span>
                    </div>
                    <div class="mt-1 inline-block text-[11px] px-2 py-0.5 rounded border {status_class}">
                        {status_text}
                    </div>
                </div>
                <input type="checkbox" {"checked" if can_travel else "disabled"} class="accent-emerald-500 w-4 h-4">
            </div>
        """

    passenger_html = f"""
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>منظومة سَابِق - بوابة المسافر الذكية</title>
        <script src="https://cdn.jsdelivr.net/npm/@tailwindcss/browser@4"></script>
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap" rel="stylesheet">
        <style>body {{ font-family: 'Cairo', sans-serif; }}</style>
    </head>
    <body class="bg-[#0b0f19] text-slate-100 min-h-screen p-6">
        <div class="max-w-4xl mx-auto">
            <header class="flex justify-between items-center bg-[#111827] p-6 rounded-2xl border border-[#1f293d] mb-8 shadow-lg">
                <div class="flex items-center gap-4">
                    <div class="w-12 h-12 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center text-2xl">
                        <i class="fa-solid fa-passport"></i>
                    </div>
                    <div>
                        <h1 class="text-xl font-bold">بوابة المسافر الذكية</h1>
                        <p class="text-xs text-slate-400">التحقق المسبق والتصريح السريع قبل الوصول للمنفذ</p>
                    </div>
                </div>
                <button onclick="location.href='/welcome-demo'" class="text-slate-400 hover:text-white text-sm flex items-center gap-2 bg-slate-800 px-4 py-2 rounded-xl border border-slate-700 transition-all">
                    <i class="fa-solid fa-arrow-left"></i> العودة للبوابة
                </button>
            </header>

            <div class="grid md:grid-cols-3 gap-6">
                <!-- بطاقة مالك المركبة (المسافر الرئيسي) -->
                <div class="bg-[#111827] p-6 rounded-2xl border border-[#1f293d] text-center">
                    <div class="w-20 h-20 bg-slate-800 rounded-full mx-auto mb-4 flex items-center justify-center text-3xl text-slate-400 border-2 border-emerald-500/40">
                        <i class="fa-solid fa-user-tie"></i>
                    </div>
                    <h2 class="font-bold text-lg">{owner_name}</h2>
                    <p class="text-xs text-slate-400 mb-2">مالك المركبة / السائق</p>
                    <p class="text-xs text-slate-400 mb-4">رقم الهوية: {owner_id}</p>
                    <div class="bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs py-2 px-3 rounded-xl mb-4">
                        <i class="fa-solid fa-circle-check"></i> الجوازات والتأمين مفعّل
                    </div>
                </div>

                <!-- تفاصيل الرحلة والتابعين المرافقين -->
                <div class="md:col-span-2 bg-[#111827] p-6 rounded-2xl border border-[#1f293d]">
                    <h3 class="font-bold text-lg mb-4 flex items-center gap-2 text-slate-200">
                        <i class="fa-solid fa-route text-emerald-400"></i> بيانات رحلة العبور والتابعين المرافقين
                    </h3>
                    
                    <div class="space-y-4">
                        <div>
                            <label class="block text-xs text-slate-400 mb-1">المنفذ الحدودي المستهدف</label>
                            <select class="w-full bg-[#0b0f19] border border-[#1f293d] rounded-xl p-3 text-sm focus:outline-none focus:border-emerald-500">
                                <optgroup label="مملكة البحرين">
                                    <option>منفذ جسر الملك فهد</option>
                                </optgroup>
                                <optgroup label="دولة الإمارات العربية المتحدة">
                                    <option>منفذ البطحاء</option>
                                </optgroup>
                                <optgroup label="دولة قطر">
                                    <option>منفذ سلوى</option>
                                </optgroup>
                                <optgroup label="دولة الكويت">
                                    <option>منفذ الخفجي</option>
                                    <option>منفذ الرقعي</option>
                                </optgroup>
                                <optgroup label="سلطنة عمان">
                                    <option>منفذ الربع الخالي</option>
                                </optgroup>
                                <optgroup label="المملكة الأردنية الهاشمية">
                                    <option>منفذ الحديثة</option>
                                    <option>منفذ حالة عمار</option>
                                    <option>منفذ الدرة</option>
                                </optgroup>
                                <optgroup label="جمهورية العراق">
                                    <option>منفذ جديدة عرعر</option>
                                </optgroup>
                                <optgroup label="الجمهورية اليمنية">
                                    <option>منفذ الوديعة</option>
                                    <option>منفذ الخضراء</option>
                                    <option>منفذ الطوال</option>
                                </optgroup>
                            </select>
                        </div>

                        <div>
                            <label class="block text-xs text-slate-400 mb-1">المركبة المسجلة</label>
                            <input type="text" value="أ ب ج 1234 (فورد تورس 2024)" readonly class="w-full bg-[#0b0f19] border border-[#1f293d] rounded-xl p-3 text-sm text-slate-300">
                        </div>

                        <div>
                            <label class="block text-xs text-slate-400 mb-2">أفراد العائلة والركاب المرافقون</label>
                            <div class="space-y-2">
                                {passengers_html_items}
                            </div>
                        </div>

                        <!-- قسم دعوة مرافق/زميل إضافي عبر رقم الجوال ونفاذ بأمان تام -->
                        <div class="p-4 bg-[#0b0f19] rounded-xl border border-emerald-500/20 mt-4">
                            <h4 class="text-xs font-bold text-emerald-400 mb-2 flex items-center gap-2">
                                <i class="fa-solid fa-user-plus"></i> دعوة زميل مرافق برحلة العبور (بأمان تام عبر رقم الجوال)
                            </h4>
                            <p class="text-[11px] text-slate-400 mb-3">أدخل رقم جوال الزميل فقط، وسيصلك إشعار بعد توثيقه هويته بنفسه عبر تطبيق نفاذ.</p>
                            
                            <div class="flex gap-2 mb-3">
                                <input type="text" id="guestPhone" placeholder="رقم الجوال (05xxxxxxxx)" class="w-full bg-[#111827] border border-[#1f293d] rounded-lg p-2.5 text-xs text-slate-200 focus:outline-none focus:border-emerald-500">
                                <button onclick="sendNafathInvite()" class="bg-emerald-600 hover:bg-emerald-500 text-white px-4 py-2.5 rounded-lg text-xs font-bold transition-all whitespace-nowrap flex items-center gap-1.5">
                                    <i class="fa-solid fa-paper-plane"></i> إرسال الدعوة
                                </button>
                            </div>
                            
                            <div id="inviteStatus" class="hidden mt-3 p-2.5 bg-emerald-500/10 border border-emerald-500/30 rounded-lg text-center text-xs text-emerald-300">
                                <i class="fa-solid fa-circle-check"></i> تم إرسال رابط التحقق بنجاح لرقم الجوال. بانتظار توثيق الزميل عبر تطبيق نفاذ...
                            </div>
                        </div>

                        <button onclick="generatePass()" class="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-bold py-3 rounded-xl transition-all shadow-lg shadow-emerald-900/30 flex items-center justify-center gap-2 mt-4">
                            <i class="fa-solid fa-qrcode"></i> إصدار تصريح العبور السريع
                        </button>
                    </div>

                    <div id="passQrResult" class="hidden mt-6 p-4 bg-slate-900 border border-emerald-500/40 rounded-xl text-center">
                        <div class="text-emerald-400 text-sm font-bold mb-2"><i class="fa-solid fa-circle-check"></i> تم إصدار التصريح بنجاح!</div>
                        <p class="text-xs text-slate-400 mb-3">يمكنك الآن التوجه مباشرة للمسار الأخضر الذكي عبر الكابينات.</p>
                        <div class="inline-block bg-white p-3 rounded-xl">
                            <i class="fa-solid fa-qrcode text-6xl text-slate-900"></i>
                        </div>
                        <p class="text-xs font-mono text-slate-400 mt-2">TOKEN: PASS-GREEN-88912</p>
                    </div>
                </div>
            </div>
        </div>

        <script>
            function sendNafathInvite() {{
                const phone = document.getElementById('guestPhone').value;
                if(!phone) {{
                    alert('الرجاء إدخال رقم جوال الزميل أولاً');
                    return;
                }}
                document.getElementById('inviteStatus').classList.remove('hidden');
            }}

            function generatePass() {{
                document.getElementById('passQrResult').classList.remove('hidden');
            }}
        </script>
    </body>
    </html>
    """
    return render_template_string(passenger_html)

@app.route('/api/verify', methods=['POST'])
def verify_vehicle():
    data = request.get_json() or {}
    plate = data.get('plate_number', '').strip()

    timestamp = datetime.datetime.now().strftime('%H:%M:%S')
    token = "SBQ-" + str(uuid.uuid4())[:8].upper()

    if not plate:
        return jsonify({
            'status_code': 'YELLOW',
            'status_title': 'مسار التدقيق (مركبة غير مسجلة)',
            'status_desc': 'لم يتم إدخال أو التقط رقم اللوحة، يلزم التدقيق اليدوي.',
            'token': token,
            'timestamp': timestamp,
            'passengers': []
        })

    conn = get_db_connection()
    cursor = conn.cursor()

    # الاستعلام عن الركاب المرتبطين باللوحة من قاعدة البيانات sabiq.db
    query = '''
        SELECT p.NationalID, p.FullName, p.Relation, p.PassportStatus, 
               p.HasSecurityRestrictions, p.HasTravelBan, p.UnpaidFines
        FROM Passengers p
        JOIN TripPassengers tp ON p.NationalID = tp.NationalID
        WHERE tp.PlateNumber = ?
    '''
    cursor.execute(query, (plate,))
    rows = cursor.fetchall()
    conn.close()

    # 1. القاعدة الأولى: إذا لم يتم العثور على اللوحة في قاعدة البيانات -> المسار الأصفر (غير مسجل مسبقاً)
    if not rows:
        return jsonify({
            'status_code': 'YELLOW',
            'status_title': 'مسار التدقيق - مركبة أو ركاب غير مسجلين',
            'status_desc': 'لم يتم العثور على إجراءات تحقق مسبقة عبر البوابة الذكية، يلزم التحقق وإضافة البصمة يدوياً.',
            'token': token,
            'timestamp': timestamp,
            'passengers': []
        })

    # تحليل حالة الركاب
    passengers_list = []
    has_red_flag = False

    for row in rows:
        passengers_list.append({
            'name': row['FullName'],
            'national_id': row['NationalID'],
            'relation': row['Relation'],
            'match_rate': '98.5%'
        })

        # 2. القاعدة الثانية: الكشف عن القيود الأمنية أو منع السفر الطارئ -> المسار الأحمر
        if row['HasTravelBan'] == 1 or row['HasSecurityRestrictions'] == 1:
            has_red_flag = True

    if has_red_flag:
        status_code = 'RED'
        status_title = 'مسار التحويل - توجيه للتفتيش الأمني'
        status_desc = 'توجد قيود أمنية أو منع سفر طارئ على أحد الركاب في المركبة.'
    else:
        # 3. القاعدة الثالثة: البيانات سليمة والركاب مسجلون مسبقاً -> المسار الأخضر
        status_code = 'GREEN'
        status_title = 'المسار الأخضر - عبور سريع مباشر'
        status_desc = 'تم التحقق المسبق من جميع البيانات والوثائق الحيوية بنجاح.'

    return jsonify({
        'status_code': status_code,
        'status_title': status_title,
        'status_desc': status_desc,
        'token': token,
        'timestamp': timestamp,
        'passengers': passengers_list
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)