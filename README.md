# ✈️ Flight Delay Analysis — Uçuş Gecikmələrinin Təhlili
<p align="center">
  <img src="Flight Delay Analysis Above the Clouds.png" width="100%">
</p>

## 📌 Layihə haqqında

Uçuşların gecikməsi sərnişinlərə, aviaşirkətlərə və hava limanlarının fəaliyyətinə təsir edən mühüm problemlərdən biridir. Gecikmələrin səbəblərini və yaranma qanunauyğunluqlarını araşdırmaq daha yaxşı planlaşdırma və qərarların qəbul edilməsinə kömək edə bilər.

**Flight Delay Analysis** ABŞ uçuş məlumatlarının təhlili, tarixi hava şəraiti məlumatları ilə zənginləşdirilməsi, statistik araşdırmaların aparılması və uçuş gecikmələrinin proqnozlaşdırılması üçün Machine Learning modellərinin hazırlanmasını əhatə edən End-to-End Data Analytics layihəsidir.

Layihə məlumatların təmizlənməsindən və SQL Server-də saxlanılmasından başlayaraq statistik təhlil, xüsusiyyətlərin yaradılması və proqnozlaşdırıcı modellərin qurulmasına qədər əsas mərhələləri əhatə edir.

## 🎯 Layihənin məqsədləri

- Aviaşirkətlər, hava limanları və həftənin günləri üzrə gecikmələri təhlil etmək.
- Hava şəraiti ilə uçuş gecikmələri arasındakı əlaqəni araşdırmaq.
- Gecikmələrlə əlaqəli əsas dəyişənləri müəyyənləşdirmək.
- Statistik testlər vasitəsilə məlumatlar arasındakı əlaqələri qiymətləndirmək.
- Machine Learning üçün yeni xüsusiyyətlər yaratmaq.
- Uçuş gecikmələrini proqnozlaşdıran təsnifat modelləri qurmaq və qiymətləndirmək.
- Analitik nəticələri vizuallaşdırmaq və Power BI vasitəsilə təqdim etmək.

📁 Layihənin strukturu

<img width="2528" height="1696" alt="data workflow (2)" src="https://github.com/user-attachments/assets/31c961b0-6cbf-4deb-91f7-9badbd41127e" />



## 🛠️ İstifadə olunan texnologiyalar

| Texnologiya | İstifadə məqsədi |
|---|---|
| Python | Məlumatların emalı, təhlili və modelləşdirmə |
| Pandas və NumPy | Məlumatların təmizlənməsi və çevrilməsi |
| SQL Server | Məlumatların saxlanılması və idarə edilməsi |
| SQLAlchemy və pymssql | Python ilə SQL Server arasında əlaqə |
| Jupyter Notebook | Analizlərin aparılması və sənədləşdirilməsi |
| SciPy | Statistik testlər |
| Scikit-learn | Machine Learning modelləri və qiymətləndirmə |
| imbalanced-learn | SMOTE vasitəsilə sinif balanssızlığının aradan qaldırılması |
| Open-Meteo API | Tarixi hava məlumatlarının əldə edilməsi |
| Power BI | Məlumatların vizuallaşdırılması və dashboard hazırlanması |
| Git və GitHub | Versiyaların idarə edilməsi və layihənin saxlanılması |

## 📂 Məlumat mənbələri

### 1. Uçuş məlumatları

Layihədə Kaggle platformasından əldə edilmiş ABŞ uçuş məlumatlarından istifadə olunur. İlkin məlumat dəsti təxminən 5 milyon sətirdən ibarətdir.

Məlumat dəstində aşağıdakı göstəricilər mövcuddur:

- Uçuş tarixi və planlaşdırılmış vaxtlar
- Aviaşirkətlər və uçuş nömrələri
- Uçuşun başlanğıc və təyinat hava limanları
- Uçuşların yola düşmə və çatma gecikmələri
- Taxi vaxtları və uçuş müddəti
- Ləğv edilmiş və istiqaməti dəyişdirilmiş uçuşlar
- Uçuş məsafəsi

### 2. Hava şəraiti məlumatları

Tarixi hava məlumatları [Open-Meteo API](https://open-meteo.com/) vasitəsilə əldə edilir.

Hava məlumatları hava limanı, tarix və vaxt əsasında uçuş məlumatları ilə birləşdirilir. Beləliklə, külək, yağıntı və digər meteoroloji göstəriciləri təhlilə daxil etmək mümkün olur.

## 🔄 Layihənin iş mərhələləri

### 1. Data Engineering və məlumatların hazırlanması

- İlkin uçuş məlumatlarının yüklənməsi və araşdırılması.
- Python və Pandas vasitəsilə məlumatların təmizlənməsi.
- Hava limanlarının identifikatorlarının kodlar və təsviri məlumatlarla uyğunlaşdırılması.
- Təhlilə uyğun olmayan qeydlərin müvafiq mərhələlərdə çıxarılması.
- Tarixi hava məlumatlarının uçuş məlumatlarına əlavə edilməsi.
- Məlumatların SQL Server-də Bronze, Silver və Gold qatları üzrə təşkil edilməsi.

### 2. SQL Server arxitekturası

Layihədə məlumatların mərhələli emalı üçün Bronze–Silver–Gold yanaşmasından istifadə olunur.

| Qat | Təyinatı |
|---|---|
| **Bronze** | İlkin və ya bazaya yeni yüklənmiş məlumatların saxlanılması |
| **Silver** | Təmizlənmiş, çevrilmiş və hava məlumatları ilə zənginləşdirilmiş məlumatların saxlanılması |
| **Gold** | Hesabatlar və analitik təhlil üçün hazırlanmış məlumatların saxlanılması |

### 3. Exploratory Data Analysis (EDA)

EDA mərhələsində aşağıdakılar araşdırılır:

- Uçuşların yola düşmə və çatma gecikmələrinin paylanması
- Aviaşirkətlər üzrə gecikmə göstəriciləri
- Həftənin günləri üzrə gecikmə fərqləri
- Hava şəraiti ilə gecikmələr arasındakı əlaqələr
- Rəqəmsal dəyişənlər arasındakı korrelyasiya
- Kənar qiymətlər (outliers)
- Hava məlumatlarında çatışmayan qiymətlər

### 4. Statistik təhlil

Məlumatlardakı əlaqələri yoxlamaq və fərqləri qiymətləndirmək üçün statistik metodlardan istifadə olunur.

- Təsviri statistika (Descriptive Statistics)
- Korrelyasiya analizi
- Chi-square müstəqillik testi
- Cramér's V ilə əlaqənin gücünün qiymətləndirilməsi
- Mann–Whitney U testi
- Kənar qiymətlərin təhlili

### 5. Feature Engineering

Machine Learning modelləri üçün yeni xüsusiyyətlər yaradılır və mövcud dəyişənlər hazırlanır.

Nümunələr:

- Uçuşun yola düşmə saatı
- Həftənin günü
- Həftəsonu göstəricisi (`IS_WEEKEND`)
- Hava şəraiti dəyişənləri
- Əvvəlki uçuşun gecikmə göstəricisi (`PREV_FLIGHT_IS_DELAYED`)

Əvvəlki uçuşun gecikmə göstəricisi eyni təyyarə ilə əlaqəli əvvəlki uçuşun gecikməsinin növbəti uçuşun gecikməsinə təsirini araşdırmaq üçün nəzərdə tutulub.

### 6. Machine Learning

Layihədə uçuş gecikməsinin proqnozlaşdırılması ikili təsnifat (Binary Classification) məsələsi kimi nəzərdən keçirilir.

**Hədəf dəyişən:** `IS_DELAYED`

- `1` — uçuşun yola düşmə gecikməsi ən azı 15 dəqiqədir.
- `0` — uçuşun yola düşmə gecikməsi 15 dəqiqədən azdır.

Ləğv edilmiş, istiqaməti dəyişdirilmiş və hədəf dəyişəni məlum olmayan uçuşlar modelin məqsədinə uyğun şəkildə ayrıca qiymətləndirilməlidir.

Machine Learning mərhələsinin əsas addımları:

1. Model üçün məlumat dəstinin hazırlanması.
2. Xüsusiyyətlərin və hədəf dəyişənin ayrılması.
3. Təlim və test dəstlərinin yaradılması.
4. Rəqəmsal və kateqorik dəyişənlərin emalı.
5. Lazım gəldikdə SMOTE vasitəsilə sinif balanssızlığının aradan qaldırılması.
6. Təsnifat modellərinin qurulması.
7. Precision, Recall, F1-score və digər metriklərlə qiymətləndirmə.
8. Xüsusiyyətlərin əhəmiyyətinin və modelin məhdudiyyətlərinin araşdırılması.

**Vacib qeyd:** SMOTE və digər öyrənilən emal addımları yalnız təlim məlumatlarına tətbiq edilməlidir. Bu, məlumat sızmasının (data leakage) qarşısını alır. Real istifadədə gələcək uçuşların proqnozlaşdırılması nəzərdə tutulursa, zaman ardıcıllığını qoruyan train/test bölgüsü daha məqsədəuyğundur.

## 📊 İlkin analitik nəticələr

EDA və statistik təhlil mərhələlərində aşağıdakı nəticələr əldə edilib:

- Təmizlənmiş məlumat dəsti təxminən **1 milyon uçuş qeydindən** ibarətdir.
- Orta yola düşmə gecikməsi təxminən **9,34 dəqiqə**, orta çatma gecikməsi isə **4,39 dəqiqədir**.
- Gecikmə göstəriciləri aviaşirkətlər arasında fərqlənir.
- Chi-square testi həftənin günü ilə gecikmə statusu arasında statistik əhəmiyyətli əlaqə göstərib. Lakin əlaqənin gücü zəifdir (Cramér's V ≈ 0,030).
- Hava şəraiti ilə gecikmə statusu arasında da statistik əhəmiyyətli əlaqə müşahidə edilib (Cramér's V ≈ 0,120).
- Təhlil edilən məlumatlarda qar şəraiti ilə əlaqəli uçuşların orta deyil, median çatma gecikməsi digər hava şəraiti qruplarından daha yüksək olub.

Bu nəticələr müşahidə olunan məlumatlara əsaslanır. Statistik əhəmiyyət səbəb-nəticə əlaqəsini sübut etmir. Nəticələr məlumatların keyfiyyətindən, çatışmayan qiymətlərdən və istifadə olunan təriflərdən asılı ola bilər.


**GitHub repozitoriyası:** [Flight-delay-analysis-E2E](https://github.com/edaletsadigov/Flight-delay-analysis-E2E)
