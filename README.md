# AI Code Stack

Codex için katmanlı geliştirme, mimari analiz, güvenlik denetimi, kalite kontrolü ve iletişim sistemi.

Bu depo uygulama kodu içermez. Kurulu agent/skill sisteminin hangi bileşenlerden oluştuğunu, bileşenlerin sorumluluklarını ve güvenli çalışma sırasını açıklar.

## Amaç

Sistem beş temel katmanı birlikte kullanır:

1. **gstack** görevin hangi aşamalardan geçeceğini belirler.
2. **ECC** her aşamanın teknik olarak nasıl uygulanacağını belirler.
3. **Graphify** gerektiğinde kod tabanını ve bağımlılıkları haritalar.
4. **Cybersecurity Skills** yalnızca somut ve özel güvenlik risklerinde derin uzmanlık sağlar.
5. **Caveman** teknik içeriği bozmadan son iletişimi kısaltır.

Temel sorumluluk ayrımı:

> gstack **ne zaman**, ECC **nasıl** sorusunu yönetir.

Bu ayrım iki büyük skill sisteminin aynı anda planlama ve orkestrasyon yaparak çakışmasını önler.

## Sistem mimarisi

```mermaid
flowchart TD
    U["Kullanıcı görevi"] --> G["gstack: görev orkestrasyonu"]
    G --> P["Planlama ve aşama seçimi"]
    P --> GR{"Mimari veya geniş etki analizi gerekli mi?"}
    GR -->|Evet| GRAPH["Graphify: bilgi grafiği ve bağımlılık analizi"]
    GR -->|Hayır| ECC["ECC: teknik uygulama"]
    GRAPH --> ECC
    ECC --> REVIEW["gstack-review"]
    REVIEW --> RISK{"Auth, ödeme, kullanıcı verisi, API veya güven sınırı var mı?"}
    RISK -->|Evet| CSO["gstack-cso"]
    RISK -->|Hayır| QA["gstack-qa"]
    CSO --> FINDING{"Somut özel risk bulundu mu?"}
    FINDING -->|Evet| ES["İlgili ECC security skill"]
    ES --> DEEP{"Daha derin uzmanlık gerekli mi?"}
    DEEP -->|Evet| CYBER["Tek bir savunma odaklı Cybersecurity skill"]
    DEEP -->|Hayır| QA
    CYBER --> QA
    FINDING -->|Hayır| QA
    QA --> VERIFY["Test ve doğrulama"]
    VERIFY --> RELEASE["gstack-ship / release"]
    RELEASE --> CAVE["Caveman: güvenli son iletişim"]
```

## Kurulu bileşenler

Denetim tarihi: **17 Temmuz 2026**

| Bileşen | Kaynak | Kurulu skill | Rol |
|---|---|---:|---|
| ECC | [affaan-m/everything-claude-code](https://github.com/affaan-m/everything-claude-code) | 278 | Teknik uzmanlık ve uygulama standartları |
| gstack | [garrytan/gstack](https://github.com/garrytan/gstack) | 54 | Planlama, review, QA ve release orkestrasyonu |
| Graphify | [Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify) | 1 | Kod tabanı bilgi grafiği ve etki analizi |
| Caveman | [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) | 7 | Son iletişim optimizasyonu |
| Cybersecurity Skills | [mukul975/Anthropic-Cybersecurity-Skills](https://github.com/mukul975/Anthropic-Cybersecurity-Skills) | 115 | Özel risklerde savunma odaklı derin uzmanlık |
| **Toplam** |  | **455 kayıt / 454 benzersiz ad** |  |

Kaynak Cybersecurity deposundaki 817 skill’in tamamı kurulmamıştır. Normal ürün geliştirmeye uygun 115 savunma skill’i seçilmiştir. Exploit, phishing, credential access, malware, persistence, evasion, lateral movement ve command-and-control odaklı skill’ler otomatik çalışma yüzeyine alınmamıştır.

## Katmanların görevleri

### 1. gstack: görev orkestrasyonu

gstack görevin hangi sırayla ilerleyeceğini yönetir:

- Ürün fikrini ve kapsamı sorgulama
- Office hours
- Autoplan
- CEO, engineering, design ve developer-experience plan review
- Hata araştırması
- Code review
- Design review
- QA
- CSO güvenlik denetimi
- Ship, release ve deployment

Örnek yönlendirmeler:

| İhtiyaç | gstack aşaması |
|---|---|
| Belirsiz ürün fikri | `office-hours` |
| Uygulama planı | `autoplan` |
| Mimari plan incelemesi | `plan-eng-review` |
| Kod incelemesi | `review` |
| Güvenlik denetimi | `cso` |
| Tarayıcı ve davranış testi | `qa` |
| Release | `ship` |
| Merge, deploy ve doğrulama | `land-and-deploy` |

gstack teknik framework kararlarının ana kaynağı değildir. Aşamayı seçer; teknik uygulamayı ECC’ye bırakır.

### 2. ECC: teknik uzmanlık

ECC, seçilen gstack aşamasının teknik olarak nasıl gerçekleştirileceğini belirler:

- Framework ve dil bilgisi
- Backend ve frontend kalıpları
- API ve veritabanı tasarımı
- Kod standartları
- Test stratejisi
- Güvenlik kuralları
- Performans
- Hata yönetimi
- Doğrulama
- Araştırma öncelikli geliştirme

ECC normal geliştirme sırasında güvenli varsayımları pasif guardrail olarak uygular. Her küçük görevde ağır güvenlik taraması başlatmaz.

### 3. Graphify: koşullu kod tabanı zekâsı

Graphify her görevde zorunlu değildir. Şu durumlarda kullanılır:

- Büyük kod tabanı
- Mimari keşif
- Modül ve dosya ilişkileri
- Bağımlılık analizi
- Şema ilişkileri
- Çağrı yolları
- Değişiklik etki analizi
- Geniş refactor

Küçük ve açıkça lokal değişikliklerde Graphify atlanır. Hazır bir `graphify-out/graph.json` varsa mimari sorular önce bilgi grafiğine sorulur.

Graphify çalışma zamanı denetiminde:

- `graphify 0.9.17` çalışıyordu.
- `graphify-mcp` binary’si çalışıyordu.
- Paralel extraction için Codex `multi_agent` özelliği açıktı.
- Denetlenen örnek projede Graphify indeksi yoktu.
- Codex MCP sunucu kaydı etkinleştirildi; `graphifyy[mcp]==0.9.17` ile gerçek stdio başlangıcı doğrulandı.

### 4. Cybersecurity Skills: dar kapsamlı uzmanlık

Bu paket ana güvenlik yöneticisi değildir. Ana güvenlik denetimini `gstack-cso` yönetir. Paket yalnızca review veya CSO tarafından belirlenmiş somut bir risk için kullanılır.

Kurulu 115 skill’in dağılımı:

| Alan | Skill |
|---|---:|
| Identity and access management | 33 |
| API security | 18 |
| DevSecOps | 17 |
| Cryptography | 15 |
| Web application security | 15 |
| Supply-chain security | 8 |
| AI security | 4 |
| Application security | 2 |
| Privacy compliance | 2 |
| Data protection | 1 |

Kullanım ilkesi:

```text
Önce gstack-cso bulgusu
Sonra ilgili ECC security skill'i
Yalnız ek derinlik gerekiyorsa tek Cybersecurity skill'i
```

Bu sıra aşırı kapsamı, yanlış pozitifleri, tekrar eden taramaları ve gereksiz token tüketimini azaltır.

### 5. Caveman: yalnızca iletişim

Caveman bir karar verici veya orkestratör değildir. Son çıktıda gereksiz tekrarları azaltabilir.

Korunması zorunlu içerikler:

- Kod
- Komutlar
- Dosya yolları
- Hata mesajları
- Güvenlik bulguları
- Test ve doğrulama kanıtları
- Riskler ve engeller
- Tasarım gerekçeleri

Güvenlik uyarılarında veya işlem sırasının yanlış anlaşılabileceği durumlarda sıkıştırma bırakılır ve açık anlatım kullanılır.

## Kayıt katmanları: Skill Registry, Knowledge Registry, Active Context, Graphify, Caveman

Beş katman farklı sorumluluklara sahiptir ve birbirinin yerine geçmez.

- **Skill Registry** (`policies/skill-loading.yaml`, `manifests/skills.json`): kurulu her skill'in kalıcı, deterministik, yeniden inşa edilebilir kataloğu. Vendor deposu, commit, checksum, alias ve metadata alanlarını taşır. Her `verify` çalıştırmasında aynı girdilerden aynı çıktı üretir.
- **Knowledge Registry** (`policies/knowledge-registry.yaml`, `manifests/knowledge-registry.json`): skill'leri, rolleri, policy'leri, vendor'ları, alias'ları, capability'leri, platform adapter'larını ve routing kurallarını kapsayan daha geniş statik mühendislik bilgisi indeksi. Konuşma geçmişini, kullanıcı görev içeriğini, agent akıl yürütmesini veya platformlar arası paylaşılan durumu **asla** içermez.
- **Active Context**: yalnızca geçerli görev için geçici, kapsamı dar çalışma kümesi. Bir skill'in içerik seviyesi (metadata → summary → partial → full) göreve göre yükselir; görev bitince context'ten düşer.
- **Graphify**: yalnızca kod tabanı zekâsıdır — sembol haritaları, modül ilişkileri, bağımlılık grafiği, çağrı zincirleri, mimari ve etki analizi. Skill hafızası, Knowledge Registry'nin yerine geçen bir şey veya platformlar arası bellek **değildir**.
- **Caveman**: yalnızca güvenli final kullanıcı mesajını kısaltır. Kod, komut, diff, JSON/YAML/SQL, test sonucu, güvenlik bulgusu, checksum veya commit hash'ine dokunmaz.

Zorunlu cümle:

> Bir skill'in active context'ten çıkarılması, skill'in sistemden silindiği veya unutulduğu anlamına gelmez.

### 5 çalışma örneği

**1. Context'ten düşme, registry'den silinme değildir**

> Bir görevde `react-reviewer` skill'i tam içerikle yüklenip kullanıldı, görev bitti ve context'ten düştü.

```text
Skill Registry'deki kayıt aynen durur (id, checksum, source_commit değişmez)
→ sonraki görevde skill yeniden taranmaz, yalnız metadata'dan bulunur
→ gerekiyorsa yeniden tam içerik seviyesine yüklenir
```

**2. Knowledge Registry, konuşma durumunu tutmaz**

> Bir önceki oturumda hangi dosyaların değiştirildiği, agent'ın o oturumdaki akıl yürütmesi bir sonraki oturuma "hafıza" olarak aktarılmak istendi.

```text
Knowledge Registry bu isteği karşılamaz (conversation_history ve agent_reasoning dışlanmıştır)
→ Claude Code oturumu Cursor'a veya Codex'e devredilmez
→ kalıcı olması gereken şey varsa checkpoint dosyası veya commit mesajı olarak yazılır
```

**3. Graphify skill hafızası değildir**

> "Graphify zaten hangi skill'lerin kurulu olduğunu biliyor, o zaman registry'yi atlayalım" varsayımı.

```text
Yanlış varsayım: Graphify yalnız kod sembolü/bağımlılık/çağrı-zinciri indeksidir
→ skill keşfi her zaman Skill Registry'den yapılır
→ Graphify yalnız büyük mimari/etki analizi gerektiğinde devreye girer
```

**4. Registry, deterministik olarak yeniden inşa edilebilir**

> `vendors/` alt modülleri sıfırdan checkout edildi (bu oturumda gerçekten yaşandı); hiçbir aktif context taşınmadı.

```text
python -m ai_code_stack.cli build-manifests aynı commit'lerden aynı 456→455 skill kaydını üretir
→ verify aynı 25 kontrolü tekrar çalıştırır
→ hiçbir görev geçmişine veya önceki context'e bağımlılık yoktur
```

**5. Caveman katmanı yapısal veriye dokunmaz**

> Kullanıcıya "testler geçti" özetini kısaltılmış caveman diliyle vermek isteniyor, ancak özet içinde ham test çıktısı, commit hash'i ve güvenlik bulgusu var.

```text
Caveman yalnız cümleleri kısaltır: "48/48 test geçti, commit ba12..., açık bulgu yok"
→ commit hash, sayı ve bulgu durumu harf harf korunur
→ JSON/diff/stack trace hiç caveman'a girmez
```

## Standart geliştirme akışı

```text
Görevi gstack sınıflandırır
→ gerekiyorsa office-hours veya autoplan
→ büyük mimari/etki analizi gerekiyorsa Graphify
→ ECC teknik uygulama skill'leri
→ gstack-review
→ riskli alan varsa gstack-cso
→ somut riskte ilgili ECC security skill'i
→ gerekirse tek Cybersecurity skill'i
→ gstack-qa
→ test ve doğrulama
→ gstack-ship / release
→ Caveman ile güvenli final iletişim
```

## Güvenlik protokolü

### Normal geliştirme

ECC güvenlik kuralları pasif guardrail olarak çalışır. Secure defaults, input validation, secret yönetimi ve güvenli framework kalıpları uygulama sırasında korunur.

### Kod tamamlandığında

`gstack-review` çalışır. Kod farkı, test kapsamı, veri güvenliği ve yapısal problemler incelenir.

### Yüksek riskli değişiklikler

Aşağıdaki alanlardan biri varsa `gstack-cso` gerekir:

- Authentication
- Authorization
- Ödeme
- Kullanıcı veya hassas veri
- Dosya yükleme
- Dış veya iç API
- Webhook
- Secret
- Yönetici yetkisi
- Yeni güven sınırı

### CSO kapsamı

`gstack-cso` şu alanları denetler:

- Git geçmişinde secret taraması
- Dependency ve supply-chain riski
- CI/CD güvenliği
- Infrastructure ve container güvenliği
- Webhook ve dış entegrasyonlar
- LLM ve agent güvenliği
- Skill supply-chain
- OWASP Top 10
- STRIDE threat model
- Authentication ve authorization
- Input validation
- SQL, command, template ve prompt injection
- Dosya yükleme noktaları
- Rate limiting
- Aktif doğrulama ve yanlış pozitif filtresi

### Release kapısı

Hedef davranış:

```text
Açık CRITICAL veya HIGH güvenlik bulgusu varsa release durur.
Bulgu giderilir veya kullanıcı tarafından açıkça risk kabulü yapılır.
Testler yeniden çalıştırılır.
Yeni doğrulama kanıtı olmadan push yapılmaz.
```

`gstack-ship` içindeki Step 16.5 artık versioned `security-release-gate.sh` dosyasını push öncesinde çalıştırır. Riskli diff için CSO raporu yoksa, rapor okunamıyorsa, raporun diff parmak izi güncel değişikliklerle eşleşmiyorsa veya çözülmemiş `CRITICAL/HIGH` bulgu varsa release hata koduyla durur. Risk sınıflandırması yapılamaması da fail-closed kabul edilir.

## Görev örnekleri

### Küçük UI değişikliği

> Bir butonun boşluğunu ve yazı boyutunu düzelt.

```text
ECC frontend/UI skill
→ lokal doğrulama
→ gerekirse kısa review/QA
```

Graphify, CSO ve Cybersecurity paketi atlanır.

### Büyük macOS tasarım görevi

> macOS için profesyonel bir DAW mixer ekranını yeniden tasarla.

```text
gstack office-hours/autoplan
→ mevcut büyük uygulamaysa Graphify
→ UI/UX
→ Apple HIG
→ Design System
→ Accessibility
→ ECC teknik uygulama
→ gstack-design-review
→ gstack-qa
→ Caveman final iletişim
```

### Backend ve authorization

> JWT tabanlı giriş sistemine rol bazlı yetkilendirme ekle.

```text
gstack-autoplan
→ gerekiyorsa Graphify
→ ECC backend ve framework security
→ uygulama ve testler
→ gstack-review
→ gstack-cso
→ somut JWT/RBAC riskinde ilgili güvenlik skill'i
→ gstack-qa
→ doğrulama
→ release
```

### Kritik ödeme güvenliği

> Ödeme API'si ve webhook doğrulamasını production öncesi denetle.

```text
gstack-cso
→ ECC API/security/test
→ gerekiyorsa Graphify
→ yalnız ilgili Cybersecurity skill'leri
→ replay, signature, idempotency ve rate-limit testleri
→ gstack-qa
→ açık kritik bulgu yoksa release
```

## Denetim sonuçları

### Sağlam alanlar

- Skill junction’ı çalışıyor.
- 455 klasörün tamamında okunabilir `SKILL.md` var.
- Eksik frontmatter yok.
- Bozuk symlink yok.
- Kaynağı belirsiz skill yok.
- ECC, gstack, Caveman ve seçili Cybersecurity skill’leri kaynaklarla dosya hash seviyesinde eşleşiyor.
- Kaynak Git çalışma ağaçları temiz.

### Bilinen eksikler

1. Her proje için otomatik Graphify indeksi bulunmuyor; bu bilinçli olarak koşullu tutuluyor ve yalnız mimari/dependency/impact analizi gerektiğinde oluşturuluyor.
2. Kaynak depolar ile kurulu skill klasörleri canlı bağlı değil; `install.sh` bu nedenle commit-sabitli `git submodule` fetch + kopyalama ve doğrulama kullanıyor.
3. `config/apply-overrides.mjs` (benchmark/graphify/gstack-ship/gstack-cso skill dosyalarını gerçek bir kurulu `skills/` dizininde yama yapan script) henüz hiçbir installer'a bağlanmadı — repoda duruyor ama `install.sh` veya `global-install.sh` onu çağırmıyor. Elle çalıştırılması gerekir: `node config/apply-overrides.mjs <skills-root> <repo-root>`.
4. Antigravity için doğrulanmış bir global config dosya formatı yok (`config_candidates` boş); bu yüzden `global-install.sh` Antigravity'ye hiçbir şey yazmaz, sadece atlar ve sebebini raporlar.

## Doğrulanan çalışma zamanı gereksinimleri

Kanonik installer saf Python (`ai_code_stack/`); Node/Bun/Codex sürüm doğrulaması yapmaz. Tek zorunlu bağımlılık `versions.lock`'taki `python_min` sürümü ve PyYAML. `global-install.sh`'ın Codex MCP kaydı adımı `graphify-mcp` binary'sinin `PATH`'te olmasını *ister* ama bulunamazsa hatasız atlar (fail-open değil, sadece o alt-adımı raporlayıp geçer).

## Öncelik kuralları

Çakışma olduğunda:

1. Sistem ve güvenlik kuralları
2. Proje `AGENTS.md` talimatları
3. gstack aşama ve süreç kararı
4. ECC teknik uygulama standardı
5. Graphify kod tabanı kanıtı
6. Özel Cybersecurity uzmanlığı
7. Caveman iletişim optimizasyonu

Graphify bir orkestratör değildir. Cybersecurity paketi ana CSO değildir. Caveman teknik karar vermez.

## Kurulum

`versions.lock` her vendor deposunun commit'ini sabitler. Kurulum üç ayrı, bağımsız adımdır: **repo-local** (`install.sh`), **global config** (`global-install.sh`) ve **skill değişimi** (`replace-skills.sh`). Üçü de `ai_code_stack/filesystem.py`'deki aynı güvenlik kuralına uyar: `atomic_write_text`, hedefte `GENERATED BY AI CODE STACK` işareti taşımayan (yani elle yazılmış) bir dosya varsa üzerine yazmayı reddeder — bu güvenlik testlerle doğrulanmıştır. `replace-skills.sh` ayrıca, üzerine yazdığı `skills/` klasörünü silmeden önce `skills.backup-<UTC-zaman-damgası>` olarak kenara taşır.

### Her bilgisayarda kolay kurulum

Tek bağımlılık Python 3 (ve `git`). Yeni bir makinede:

```bash
git clone --recursive https://github.com/imyigo/ai-code-stack.git
cd ai-code-stack
./install.sh && ./global-install.sh --apply && ./replace-skills.sh --apply
```

`--recursive` unutulursa sorun değil: `install.sh` zaten eksik submodule'leri kendi çeker.

- **macOS:** klonladıktan sonra `AI Code Stack Kur.command` dosyasına çift tıkla. Terminal açılır, sırayla 3 adımı çalıştırır, her global/skill adımından önce onay ister.
- **Windows:** `AI Code Stack Kur.bat` dosyasına çift tıkla. Aynı akış PowerShell üzerinden.

### Elle, terminalden

```bash
./install.sh                    # repo-local: manifest + adapter üretimi, eksik submodule'leri çeker
./global-install.sh --apply     # opsiyonel: kurulu platformlara (Codex/Claude Code/Cursor) global dosya yazar
./replace-skills.sh --apply     # opsiyonel: ~/.claude/skills ve ~/.codex/skills'i bu repodaki 455 skill ile değiştirir
```

Windows PowerShell'de:

```powershell
scripts\install.ps1
scripts\global-install.ps1 -Apply
scripts\replace-skills.ps1 -Apply
```

`install.sh` (→ `ai_code_stack.installer.install`):

1. `versions.lock`'taki minimum Python sürümünü doğrular.
2. `vendors/*` altında boş/eksik olan submodule'leri `git submodule update --init` ile çeker (zaten doluysa dokunmaz).
3. 11 manifest'i (`manifests/*.json`) ve 4 platform için adapter dosyalarını (`adapters/*`) deterministik olarak yeniden üretir — hepsi repo içinde kalır.
4. Uygulamadan önce `backups/<timestamp>/` altına `manifests`, `adapters`, `versions.lock`, `AGENTS.md`, `CLAUDE.md` yedeklenir; bir adım patlarsa otomatik `rollback` çalışır.
5. `ai_code_stack.cli verify`'ı fail-closed olarak çalıştırır.

`global-install.sh --apply` (→ `ai_code_stack.global_install.global_install`) — repo dışına yazan, ekleme-türü (additive) adım, bu yüzden varsayılan `--apply` olmadan yalnızca dry-run rapor verir:

- **Codex** kuruluysa (`~/.codex/` var): `config/AGENTS.md` içeriğini `~/.codex/AGENTS.md`'ye yazar, `graphify-mcp` `PATH`'te bulunursa `~/.codex/config.toml`'a `[mcp_servers.graphify]` bloğunu ekler (dosyanın geri kalanına dokunmadan).
- **Claude Code** kuruluysa (`~/.claude/` var): üretilmiş role dosyalarını `~/.claude/agents/*.md` altına yazar.
- **Cursor** kuruluysa (`~/.cursor/` var): `~/.cursor/rules/ai-code-stack.mdc` yazar.
- **Antigravity**: doğrulanmış global config formatı olmadığı için her zaman atlanır, sebebi rapora yazılır.
- Bir platform kurulu değilse (ilgili `~/.codex`, `~/.claude`, `~/.cursor` yoksa) o platform tamamen atlanır.
- Elle yazılmış bir dosya zaten aynı yoldaysa **asla üzerine yazılmaz**, `skipped` listesinde raporlanır.

`replace-skills.sh --apply` (→ `ai_code_stack.replace_skills.replace_skills`) — **değiştirme** türü adım, `global-install`'dan farklı olarak var olan içeriği bu repodaki setle bire bir eşitler:

- **Claude Code** (`~/.claude/skills`) ve **Codex** (`~/.codex/skills`) kuruluysa: mevcut `skills/` klasörü `skills.backup-<zaman>` olarak yeniden adlandırılır (taşınır, silinmez), sonra `manifests/skills.json`'daki 455 skill tek tek kopyalanır.
- **Antigravity**: bu makinede doğrulanmış bir skill dizini olmadığı için (`~/Library/Application Support/Antigravity` yalnız uygulama önbelleği içerir) her zaman atlanır.
- **Cursor** bu komutun kapsamında değil; `global-install.sh` zaten additive bir kural dosyası yazıyor.
- Geri almak için: `rm -rf ~/.claude/skills && mv ~/.claude/skills.backup-<zaman> ~/.claude/skills` (Codex için aynısı `~/.codex` altında).

## Doğrulama

```bash
./verify.sh
# eşdeğeri: python -m ai_code_stack.cli verify
```

`ai_code_stack.verifier.verify` fail-closed 25 kontrol çalıştırır: `versions.lock` şeması, vendor submodule pin+clean durumu, toplam/tekil skill sayısı, benchmark alias routing, 18 ortak rol, cross-platform delegation kapalı, agent limitleri, Graphify koşullu routing, Caveman sınırı, 75 adapter çıktısı, 11 manifest'in varlığı ve şema versiyonu, checksum eşleşmesi, security gate fail-closed doğru tablosu. Herhangi bir kontrol `fail` dönerse üst `status` `error` olur ve `next_actions` push'u engeller.

## Sonuç

Kurulu yapı kullanılabilir durumdadır. En önemli mimari karar, gstack ile ECC’nin sorumluluklarının ayrılmasıdır:

- **gstack:** görev sırası, review, QA ve release
- **ECC:** teknik uygulama, test, güvenlik ve doğrulama yöntemi
- **Graphify:** gerektiğinde kod tabanı kanıtı
- **Cybersecurity Skills:** özel risklerde derin savunma uzmanlığı
- **Caveman:** yalnızca güvenli son iletişim

Bu yapı doğru kullanıldığında yüksek kalite sağlar; bütün skill’lerin her görevde aynı anda çalıştırılması ise kaliteyi artırmak yerine tekrar, çakışma ve token maliyeti yaratır.
