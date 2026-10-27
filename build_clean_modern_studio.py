# -*- coding: utf-8 -*-
"""
build_clean_modern_studio.py:
Builds the complete modernized VinFast Quotation Web Studio index.html
with Elementor-inspired design, futuristic EV automotive styling,
smooth tactile click-release interactions, and 100% functional correctness.
"""
import json
import os
import re

BASE_DIR = r"C:\Users\PC\.gemini\antigravity\scratch\vinfast-baogia"
JSON_PATH = os.path.join(BASE_DIR, "data_da_bo_sung_phu_kien_combo.json")
BACKUP_PATH = os.path.join(BASE_DIR, "index.html.v65_backup")
OUTPUT_PATH = os.path.join(BASE_DIR, "index.html")

# 1. Load data
with open(JSON_PATH, "r", encoding="utf-8") as f:
    shared_data = json.load(f)

cars_json = json.dumps(shared_data.get("cars", []), ensure_ascii=False)
accs_json = json.dumps(shared_data.get("accessories", []), ensure_ascii=False)
promos_json = json.dumps(shared_data.get("promos", []), ensure_ascii=False)
combos_json = json.dumps(shared_data.get("accessoryCombos", []), ensure_ascii=False)
tabs_json = json.dumps(shared_data.get("accessorySaleTabs", []), ensure_ascii=False)

# 2. Extract core JS logic from backup
with open(BACKUP_PATH, "r", encoding="utf-8") as f:
    backup_text = f.read()

s1_start = backup_text.find("const PHI_DANG_KY = 140000;")
s1_end = backup_text.find("</script>", s1_start)
core_js = backup_text[s1_start:s1_end].strip()

# Replace embedded dataset in core_js using lambdas to prevent backslash escape issues
dc_pattern = re.compile(r"const defaultCars = \[.*?\];", re.DOTALL)
core_js = dc_pattern.sub(lambda m: f"const defaultCars = {cars_json};", core_js, count=1)

acc_pattern = re.compile(r"const defaultAccessories = \[.*?\];", re.DOTALL)
if acc_pattern.search(core_js):
    core_js = acc_pattern.sub(lambda m: f"const defaultAccessories = {accs_json};", core_js, count=1)
else:
    core_js = core_js.replace("const initPromos = [", f"const defaultAccessories = {accs_json};\n        const initPromos = [")

promos_pattern = re.compile(r"const initPromos = \[.*?\];", re.DOTALL)
core_js = promos_pattern.sub(lambda m: f"const initPromos = {promos_json};", core_js, count=1)

combos_pattern = re.compile(r"const REFERENCE_ACCESSORY_COMBOS = \[.*?\];", re.DOTALL)
core_js = combos_pattern.sub(lambda m: f"const REFERENCE_ACCESSORY_COMBOS = {combos_json};", core_js, count=1)

tabs_pattern = re.compile(r"const REFERENCE_ACCESSORY_SALE_TABS = \[.*?\];", re.DOTALL)
core_js = tabs_pattern.sub(lambda m: f"const REFERENCE_ACCESSORY_SALE_TABS = {tabs_json};", core_js, count=1)

# Remove animateNumber completely and replace with direct setPriceText
anim_start = core_js.find('function animateNumber(')
anim_end = core_js.find('function setConsoleTab(')
if anim_start != -1 and anim_end != -1:
    set_price_replacement = """function setPriceText(id, text) {
            const el = document.getElementById(id);
            if (!el) return;
            if (el.innerText !== text) {
                el.innerText = text;
                el.classList.remove('value-updated-pulse');
                void el.offsetWidth;
                el.classList.add('value-updated-pulse');
            }
        }\n\n        """
    core_js = core_js[:anim_start] + set_price_replacement + core_js[anim_end:]

# Replace any remaining animateNumber calls in updateQuotationUI
replacements = [
    ("animateNumber('quote-price-listed', calc.listPrice);", "setPriceText('quote-price-listed', formatMoney(calc.listPrice));"),
    ("animateNumber('quote-discount', Math.max(0, Number(calc.totalDiscount || 0)));", "setPriceText('quote-discount', formatMoney(Math.max(0, Number(calc.totalDiscount || 0))));"),
    ("animateNumber('quote-invoice-discount', Math.max(0, Number(calc.invoiceDiscount || 0)), '- ');", "setPriceText('quote-invoice-discount', '- ' + formatMoney(Math.max(0, Number(calc.invoiceDiscount || 0))));"),
    ("animateNumber('quote-invoice-price', calc.invoicePrice);", "setPriceText('quote-invoice-price', formatMoney(calc.invoicePrice));"),
    ("animateNumber('quote-payment-discount', Math.max(0, Number(calc.paymentDiscount || 0)), '- ');", "setPriceText('quote-payment-discount', '- ' + formatMoney(Math.max(0, Number(calc.paymentDiscount || 0))));"),
    ("animateNumber('quote-price-final', calc.invoicePrice);", "setPriceText('quote-price-final', formatMoney(calc.invoicePrice));"),
    ("animateNumber('quote-tax', calc.tax);", "setPriceText('quote-tax', formatMoney(calc.tax));"),
    ("animateNumber('quote-phi-dang-ky', calc.phiDangKy);", "setPriceText('quote-phi-dang-ky', formatMoney(calc.phiDangKy));"),
    ("animateNumber('quote-phi-dang-kiem', calc.phiDangKiem);", "setPriceText('quote-phi-dang-kiem', formatMoney(calc.phiDangKiem));"),
    ("animateNumber('quote-phi-duong-bo', calc.dBo);", "setPriceText('quote-phi-duong-bo', formatMoney(calc.dBo));"),
    ("animateNumber('quote-phi-tnds', calc.tnds);", "setPriceText('quote-phi-tnds', formatMoney(calc.tnds));"),
    ("animateNumber('quote-phi-dich-vu', adj.registrationService);", "setPriceText('quote-phi-dich-vu', formatMoney(adj.registrationService));"),
    ("animateNumber('quote-bu-thue', calc.bu);", "setPriceText('quote-bu-thue', formatMoney(calc.bu));"),
    ("animateNumber('quote-bh-vc', calc.bhVal);", "setPriceText('quote-bh-vc', formatMoney(calc.bhVal));"),
    ("animateNumber('quote-acc-cost', calc.totAcc);", "setPriceText('quote-acc-cost', formatMoney(calc.totAcc));"),
    ("animateNumber('quote-reg-total', calc.netReg);", "setPriceText('quote-reg-total', formatMoney(calc.netReg));"),
    ("animateNumber('quote-total', calc.totOnRoad);", "setPriceText('quote-total', formatMoney(calc.totOnRoad));")
]
for src, dst in replacements:
    core_js = core_js.replace(src, dst)

# Enhance updateQuotationUI to also update the Studio Top Command Bar badge and Hero Card
enhance_target = "scheduleQuotePriceFit(document);"
enhance_replacement = """scheduleQuotePriceFit(document);
            // Update Studio Top Command Bar & Console Hero Card
            const qb = document.getElementById('quick-car-badge');
            if (qb && car) {
                qb.innerHTML = `<span class=\"text-white font-black\">${car.name} ${car.version}</span> <span class=\"text-cyan-400 font-bold\">• ${formatMoney(calc.totOnRoad)}</span>`;
            }
            const hc = document.getElementById('studio-hero-model');
            if (hc && car) hc.innerText = `${car.name} ${car.version} ${car.year || ''}`.trim();
            const hp = document.getElementById('studio-hero-price');
            if (hp && car) hp.innerText = formatMoney(calc.totOnRoad);
            const cs = document.getElementById('consoleCarSelect');
            if (cs && cs.value !== car.id) cs.value = car.id;
"""
core_js = core_js.replace(enhance_target, enhance_replacement, 1)

# Ensure consoleCarSelect is populated in renderDropdown
render_dd_target = "function renderDropdown() { const s=document.getElementById('carSelect'), v=s.value; s.innerHTML=carList.map(c=>`<option value=\"${c.id}\">${c.name} ${c.version}</option>`).join(''); if(v&&carList.find(c=>c.id===v))s.value=v; }"
render_dd_replacement = """function renderDropdown() { 
            const s = document.getElementById('carSelect'); 
            const cs = document.getElementById('consoleCarSelect');
            const v = s ? s.value : ''; 
            const optionsHtml = carList.map(c => `<option value=\"${c.id}\">${c.name} ${c.version}</option>`).join('');
            if (s) { s.innerHTML = optionsHtml; if (v && carList.find(c => c.id === v)) s.value = v; }
            if (cs) { cs.innerHTML = optionsHtml; if (v && carList.find(c => c.id === v)) cs.value = v; }
        }
        function handleConsoleCarChange(val) {
            const s = document.getElementById('carSelect');
            if (s && s.value !== val) {
                s.value = val;
                handleCarSelectionChange();
            }
        }"""
core_js = core_js.replace(render_dd_target, render_dd_replacement, 1)

# Injected Magic Studio Toast & Robust toggleLiveCustomize
toggle_target = "function toggleLiveCustomize(s) {"
toggle_idx = core_js.find(toggle_target)
if toggle_idx != -1:
    toggle_end = core_js.find("function resetLiveCustomize()", toggle_idx)
    new_toggle_js = """function showMagicToast(msg, icon = '✨') {
            let t = document.getElementById('magic-studio-toast');
            if (!t) {
                t = document.createElement('div');
                t.id = 'magic-studio-toast';
                t.className = 'fixed top-5 left-1/2 -translate-x-1/2 z-[1001] pointer-events-none transition-all duration-300 opacity-0 translate-y-[-10px] flex items-center gap-2.5 px-4 py-2 rounded-full bg-slate-900/95 backdrop-blur-xl border border-cyan-400/40 text-white text-xs font-bold shadow-[0_10px_30px_rgba(6,182,212,0.35)]';
                document.body.appendChild(t);
            }
            t.innerHTML = `<span class="text-base">${icon}</span> <span>${msg}</span>`;
            t.style.opacity = '1';
            t.style.transform = 'translate(-50%, 0)';
            clearTimeout(t._timer);
            t._timer = setTimeout(() => {
                t.style.opacity = '0';
                t.style.transform = 'translate(-50%, -10px)';
            }, 2300);
        }

        function toggleLiveCustomize(s) {
            const p = document.getElementById('live-customize-panel');
            const b = document.getElementById('live-customize-backdrop');
            const c = document.getElementById('customize-toggle');
            if (!p) return;
            if (c) c.checked = !!s;
            p.classList.toggle('hidden-panel', !s);
            if (b) b.classList.toggle('hidden', !s);
            if (s) {
                fillLiveCustomizePanel();
                setupLive();
                p.scrollTop = 0;
                showMagicToast('Đang mở bảng tùy chỉnh biểu phí...', '⚙️');
            }
        }\n\n        """
    core_js = core_js[:toggle_idx] + new_toggle_js + core_js[toggle_end:]
    print("6.1 Injected robust toggleLiveCustomize & showMagicToast!")

# Connect Escape key to close modal
escape_handler = """
        window.addEventListener('keydown', (e) => {
            if (e.key === 'Escape') {
                const p = document.getElementById('live-customize-panel');
                if (p && !p.classList.contains('hidden-panel')) {
                    toggleLiveCustomize(false);
                }
            }
        });
"""
core_js += escape_handler


# Enhance renderQuoteColorSwatches with console swatches sync & clean UTF-8
rsw_old_start = core_js.find('function renderQuoteColorSwatches(car)')
rsw_old_end = core_js.find('async function compressImageFile', rsw_old_start)
if rsw_old_start != -1 and rsw_old_end != -1:
    clean_rsw = """function renderQuoteColorSwatches(car) {
            if (!car) return;
            const cfg = getVehicleColorConfig(car) || { basic:[], premium:[], surcharge:0 };
            const selected = getSelectedColorInfo(car)?.name || '';
            const basicEl = document.getElementById('quote-basic-color-swatches');
            const premiumEl = document.getElementById('quote-premium-color-swatches');
            const premiumWrap = document.getElementById('quote-premium-color-wrap');
            const premiumLabel = document.getElementById('quote-premium-color-label');
            const selectedEl = document.getElementById('quote-selected-color');

            if (selectedEl) selectedEl.textContent = selected || '—';

            // Đồng bộ nhãn màu & swatches trên Left Studio Console
            const consoleColorLabel = document.getElementById('console-selected-color-name');
            if (consoleColorLabel) consoleColorLabel.textContent = selected || '—';
            const consoleSwatches = document.getElementById('console-color-swatches');

            const makeChip = (name, premium=false) => {
                const active = name === selected;
                const activeCls = active ? 'is-active' : 'border border-slate-300/90';
                const title = premium && Number(cfg.surcharge || 0) > 0
                    ? `${name} · +${formatMoney(cfg.surcharge)}`
                    : name;
                return `<button type="button" onclick="syncCarColor(${JSON.stringify(name).replace(/"/g,'&quot;')})" title="${title.replace(/"/g,'&quot;')}" class="el-color-swatch ${activeCls}" style="background:${carColorCss(name)}"></button>`;
            };

            if (basicEl) basicEl.innerHTML = (cfg.basic || []).map(n => makeChip(n, false)).join('');
            if (premiumEl) premiumEl.innerHTML = (cfg.premium || []).map(n => makeChip(n, true)).join('');

            if (consoleSwatches) {
                const allColors = [...(cfg.basic || []), ...(cfg.premium || [])];
                if (allColors.length > 0) {
                    consoleSwatches.innerHTML = allColors.map(n => makeChip(n, (cfg.premium || []).includes(n))).join('');
                } else {
                    consoleSwatches.innerHTML = '<span class="text-xs text-gray-400 italic">Mặc định theo xe</span>';
                }
            }

            if (premiumWrap) premiumWrap.classList.toggle('hidden', !(cfg.premium || []).length);
            if (premiumLabel) {
                premiumLabel.textContent = Number(cfg.surcharge || 0) > 0
                    ? `Màu nâng cao + ${formatMoney(cfg.surcharge)}`
                    : 'Màu nâng cao';
            }
        }\n\n        """
    core_js = core_js[:rsw_old_start] + clean_rsw + core_js[rsw_old_end:]
    print("4.1 Injected clean renderQuoteColorSwatches with console sync!")

# Enhance savePreviewPdf with perfect A4 1-page fit
pdf_slice_marker = "const pxPerMm = canvas.width / usableWidth;"
pdf_slice_start = core_js.find(pdf_slice_marker)
if pdf_slice_start != -1:
    pdf_slice_end = core_js.find("const car = carList.find(c => c.id ===", pdf_slice_start)
    clean_pdf_fit = """const canvasAspect = canvas.width / canvas.height;
                const a4Aspect = usableWidth / usableHeight;

                let pdfW, pdfH, xOff, yOff;
                if (canvasAspect < a4Aspect) {
                    pdfH = usableHeight;
                    pdfW = usableHeight * canvasAspect;
                    xOff = margin + (usableWidth - pdfW) / 2;
                    yOff = margin;
                } else {
                    pdfW = usableWidth;
                    pdfH = usableWidth / canvasAspect;
                    xOff = margin;
                    yOff = margin + (usableHeight - pdfH) / 2;
                }

                const imgData = canvas.toDataURL('image/jpeg', 0.96);
                pdf.addImage(imgData, 'JPEG', xOff, yOff, pdfW, pdfH, undefined, 'FAST');\n\n                """
    core_js = core_js[:pdf_slice_start] + clean_pdf_fit + core_js[pdf_slice_end:]
    print("4.2 Injected clean A4 1-page fit into savePreviewPdf!")

# Enhance applyExportTextLayout with explicit text and swatch clearances
layout_marker = "function applyExportTextLayout(clone, mode = 'full') {"
layout_start = core_js.find(layout_marker)
if layout_start != -1:
    layout_end = core_js.find("function buildFocusedExportClone()", layout_start)
    clean_layout_func = """function applyExportTextLayout(clone, mode = 'full') {
            if (!clone) return;
            try {
                clone.style.textRendering = 'geometricPrecision';
                clone.style.webkitFontSmoothing = 'antialiased';

                // Khóa header không bao giờ bị rớt dòng SĐT đè lên đường kẻ xanh
                const headerP = clone.querySelector('header p');
                if (headerP) {
                    headerP.style.whiteSpace = 'nowrap';
                    headerP.style.lineHeight = '20px';
                    headerP.style.margin = '0';
                }

                // Khóa thẻ giá niêm yết không bị rớt chữ đè dòng
                clone.querySelectorAll('.quote-price-row').forEach(row => {
                    row.style.minHeight = '36px';
                    row.style.height = 'auto';
                    row.style.display = 'flex';
                    row.style.justifyContent = 'space-between';
                    row.style.alignItems = 'center';
                    row.style.marginBottom = '4px';
                    row.style.lineHeight = '20px';
                    if (row.children[0]) row.children[0].style.whiteSpace = 'nowrap';
                    if (row.children[1]) row.children[1].style.whiteSpace = 'nowrap';
                });

                // Khóa bảng sạc & bảo hành
                const chargingPanel = clone.querySelector('#charging-promo-panel');
                if (chargingPanel) {
                    chargingPanel.querySelectorAll('h3').forEach(h => {
                        h.style.whiteSpace = 'nowrap';
                        h.style.lineHeight = '22px';
                        h.style.margin = '0 0 2px 0';
                    });
                }
                const warrantyPanel = clone.querySelector('#warranty-panel');
                if (warrantyPanel) {
                    warrantyPanel.querySelectorAll('h3').forEach(h => {
                        h.style.whiteSpace = 'nowrap';
                        h.style.lineHeight = '22px';
                        h.style.margin = '0 0 2px 0';
                    });
                    const subtitle = warrantyPanel.querySelector('#warranty-subtitle');
                    if (subtitle) {
                        subtitle.style.whiteSpace = 'nowrap';
                        subtitle.style.lineHeight = '18px';
                        subtitle.style.margin = '0';
                    }
                }

                // Khóa màu sắc swatches luôn có kích thước chuẩn khi chụp ảnh
                clone.querySelectorAll('.el-color-swatch').forEach(swatch => {
                    swatch.style.width = '32px';
                    swatch.style.height = '32px';
                    swatch.style.borderRadius = '8px';
                    swatch.style.display = 'inline-block';
                    swatch.style.border = '2px solid #ffffff';
                    swatch.style.boxShadow = '0 1px 4px rgba(0,0,0,0.25)';
                });

                // Khóa footer tổng giá lăn bánh không đè dòng
                const footerH2 = clone.querySelector('.quote-total-footer h2');
                if (footerH2) {
                    footerH2.style.whiteSpace = 'nowrap';
                    footerH2.style.lineHeight = '32px';
                    footerH2.style.margin = '0 0 4px 0';
                }
                const footerP = clone.querySelector('.quote-total-footer p');
                if (footerP) {
                    footerP.style.whiteSpace = 'nowrap';
                    footerP.style.lineHeight = '18px';
                    footerP.style.margin = '0';
                }

                // Khóa các gạch đầu dòng thông số xe gọn gàng
                clone.querySelectorAll('#quote-car-specs li').forEach(li => {
                    li.style.lineHeight = '15px';
                    li.style.marginBottom = '5px';
                });
            } catch (err) {
                console.warn('applyExportTextLayout error:', err);
            }
        }\n\n        """
    core_js = core_js[:layout_start] + clean_layout_func + core_js[layout_end:]
    print("4.3 Injected clean applyExportTextLayout!")


# Add studio zoom & helpers
studio_helpers = """
        // ================== STUDIO CANVAS ZOOM & FIT ==================
        let currentQuoteScale = 1;
        function setQuoteViewScale(scale) {
            currentQuoteScale = scale;
            const el = document.getElementById('capture-area');
            const shell = document.getElementById('quote-live-shell');
            if (!el || !shell) return;
            
            let target = 1;
            if (scale === 'fit') {
                const containerWidth = shell.parentElement ? shell.parentElement.clientWidth : window.innerWidth;
                const available = Math.max(340, containerWidth - 32);
                target = Math.min(1, available / 1024);
            } else {
                target = Number(scale) || 1;
            }
            
            el.style.transform = target === 1 ? 'none' : `scale(${target})`;
            el.style.transformOrigin = 'top center';
            
            const scaledHeight = el.offsetHeight * target;
            if (target !== 1) {
                shell.style.height = `${scaledHeight + 35}px`;
            } else {
                shell.style.height = 'auto';
            }
            
            document.querySelectorAll('.zoom-pill-btn').forEach(btn => {
                const match = btn.dataset.scale == scale;
                btn.classList.toggle('bg-blue-600', match);
                btn.classList.toggle('text-white', match);
                btn.classList.toggle('border-blue-600', match);
                btn.classList.toggle('bg-white', !match);
                btn.classList.toggle('text-slate-700', !match);
                btn.classList.toggle('border-slate-200', !match);
            });
        }
        
        function autoFitQuoteShell() {
            if (window.innerWidth < 1280) {
                setQuoteViewScale('fit');
            } else {
                setQuoteViewScale(1);
            }
        }

        function resetDefaultDatasetFromEmbedded() {
            if (!confirm('Khôi phục toàn bộ dữ liệu Xe, Phụ Kiện và CTKM gốc chuẩn 2026? Dữ liệu tùy chỉnh cũ trong trình duyệt sẽ được làm mới.')) return;
            localStorage.removeItem('vinfast_cars_v3');
            localStorage.removeItem('vinfast_accessories_v2');
            localStorage.removeItem('vinfast_promos_v1');
            localStorage.removeItem('vinfast_accessory_combos_v1');
            localStorage.removeItem('vinfast_accessory_sale_tabs_v1');
            localStorage.removeItem('vinfast_quote_adj_v3');
            
            carList = [...defaultCars];
            accList = [...(typeof defaultAccessories !== 'undefined' ? defaultAccessories : [])];
            promoList = [...initPromos];
            accessoryCombos = [...(typeof REFERENCE_ACCESSORY_COMBOS !== 'undefined' ? REFERENCE_ACCESSORY_COMBOS : [])];
            accessorySaleTabs = [...(typeof REFERENCE_ACCESSORY_SALE_TABS !== 'undefined' ? REFERENCE_ACCESSORY_SALE_TABS : [])];
            quoteAdjustments = {};
            
            localStorage.setItem('vinfast_cars_v3', JSON.stringify(carList));
            localStorage.setItem('vinfast_accessories_v2', JSON.stringify(accList));
            localStorage.setItem('vinfast_promos_v1', JSON.stringify(promoList));
            localStorage.setItem('vinfast_accessory_combos_v1', JSON.stringify(accessoryCombos));
            localStorage.setItem('vinfast_accessory_sale_tabs_v1', JSON.stringify(accessorySaleTabs));
            
            refreshSharedDataUI();
            alert('Đã khôi phục bộ dữ liệu gốc chuẩn 2026!');
        }
"""
core_js += studio_helpers

motion_layer_js = """
/* Elementor & Cyber Motion Layer: Ripple, Parallax 3D Tilt, Auto-fit */
(function () {
    const fine = matchMedia('(hover: hover) and (pointer: fine)').matches;
    const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;

    // Ripple click effect on tactile controls
    document.addEventListener('pointerdown', function (e) {
        const t = e.target.closest && e.target.closest('.tactile-btn, .tactile-pill, button, label.cursor-pointer');
        if (!t || reduce) return;
        const r = t.getBoundingClientRect(), s = Math.max(r.width, r.height);
        const d = document.createElement('span');
        d.className = 'el-ripple';
        d.style.cssText = 'width:' + s + 'px;height:' + s + 'px;left:' + (e.clientX - r.left - s / 2) + 'px;top:' + (e.clientY - r.top - s / 2) + 'px';
        t.style.position = t.style.position === 'absolute' || t.style.position === 'fixed' ? t.style.position : 'relative';
        t.style.overflow = 'hidden';
        t.appendChild(d);
        setTimeout(function () { d.remove(); }, 650);
    }, { passive: true });

    if (fine && !reduce) {
        // 3D tilt on car showroom stage
        document.addEventListener('pointermove', function (e) {
            const stage = e.target.closest && e.target.closest('.car-stage-bg');
            const img = document.getElementById('quote-car-img');
            if (stage && img && stage.closest('#capture-area')) {
                const r = stage.getBoundingClientRect();
                const px = (e.clientX - r.left) / r.width - 0.5;
                const py = (e.clientY - r.top) / r.height - 0.5;
                img.style.setProperty('--ry', (px * 8).toFixed(2) + 'deg');
                img.style.setProperty('--rx', (-py * 5).toFixed(2) + 'deg');
            }
        }, { passive: true });

        document.addEventListener('pointerout', function (e) {
            const stage = e.target.closest && e.target.closest('.car-stage-bg');
            if (stage && !stage.contains(e.relatedTarget)) {
                const img = document.getElementById('quote-car-img');
                if (img) { img.style.setProperty('--rx', '0deg'); img.style.setProperty('--ry', '0deg'); }
            }
        }, { passive: true });
    }

    // Auto-fit responsive trigger
    window.addEventListener('resize', function () {
        if (typeof autoFitQuoteShell === 'function') autoFitQuoteShell();
    });
    window.addEventListener('load', function () {
        if (typeof autoFitQuoteShell === 'function') {
            autoFitQuoteShell();
            setTimeout(autoFitQuoteShell, 300);
        }
    });
    document.addEventListener('DOMContentLoaded', function () {
        if (typeof autoFitQuoteShell === 'function') autoFitQuoteShell();
    });
})();
"""

# Assemble the whole HTML file
html_template = f"""<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <title>VINFAST THẾ TÀI - Studio Báo Giá Chuẩn 2026</title>
    <!-- Google Fonts: Inter, Plus Jakarta Sans, Space Grotesk, JetBrains Mono -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&family=JetBrains+Mono:wght@500;700;800&family=Plus+Jakarta+Sans:wght@400;500;600;700;800;900&family=Space+Grotesk:wght@600;700;800&display=swap" rel="stylesheet">
    
    <!-- Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    
    <!-- Libraries for HD Image & PDF Export -->
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/html-to-image@1.11.11/dist/html-to-image.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>

    <script>
        tailwind.config = {{
            theme: {{
                extend: {{
                    fontFamily: {{
                        sans: ['Plus Jakarta Sans', 'Inter', 'sans-serif'],
                        display: ['Space Grotesk', 'Plus Jakarta Sans', 'sans-serif'],
                        mono: ['JetBrains Mono', 'monospace']
                    }},
                    colors: {{
                        brand: {{
                            primary: '#1464F4',
                            cyan: '#00D2FF',
                            dark: '#0B1120',
                            surface: '#F8FAFC'
                        }}
                    }}
                }}
            }}
        }}
    </script>
    
    <style>
        body {{
            background-color: #F8FAFC;
            color: #0F172A;
            font-family: 'Plus Jakarta Sans', 'Inter', sans-serif;
            margin: 0;
            padding: 0;
            min-height: 100vh;
            overflow-x: hidden;
        }}

        /* Ambient Aurora Glow */
        .aurora-bg-wrap {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            overflow: hidden;
            pointer-events: none;
            z-index: 0;
        }}
        .aurora-orb {{
            position: absolute;
            border-radius: 50%;
            filter: blur(140px);
            opacity: 0.12;
            animation: orbFloat 22s infinite alternate ease-in-out;
        }}
        .aurora-orb-1 {{
            width: 650px;
            height: 650px;
            background: radial-gradient(circle, #1464F4 0%, #06B6D4 100%);
            top: -150px;
            left: -100px;
        }}
        .aurora-orb-2 {{
            width: 550px;
            height: 550px;
            background: radial-gradient(circle, #8B5CF6 0%, #3B82F6 100%);
            bottom: -100px;
            right: -100px;
            animation-delay: -7s;
        }}
        .aurora-orb-3 {{
            width: 480px;
            height: 480px;
            background: radial-gradient(circle, #00D2FF 0%, #10B981 100%);
            top: 40%;
            left: 55%;
            opacity: 0.08;
            animation-delay: -14s;
        }}
        @keyframes orbFloat {{
            0% {{ transform: translate(0, 0) scale(1); }}
            50% {{ transform: translate(40px, 30px) scale(1.08); }}
            100% {{ transform: translate(-30px, 50px) scale(0.95); }}
        }}

        /* Tactile Click & Release Micro-Interactions ("nhấp nhả") */
        .tactile-btn {{
            transition: transform 0.16s cubic-bezier(0.34, 1.56, 0.64, 1), 
                        box-shadow 0.16s cubic-bezier(0.34, 1.56, 0.64, 1), 
                        filter 0.16s ease,
                        background-color 0.16s ease;
            user-select: none;
            -webkit-user-select: none;
            cursor: pointer;
            will-change: transform, box-shadow;
        }}
        .tactile-btn:hover {{
            transform: translateY(-2px);
            filter: brightness(1.05);
        }}
        .tactile-btn:active {{
            transform: translateY(1.5px) scale(0.965);
            filter: brightness(0.95);
        }}

        .tactile-card {{
            transition: transform 0.22s cubic-bezier(0.16, 1, 0.3, 1),
                        box-shadow 0.22s cubic-bezier(0.16, 1, 0.3, 1),
                        border-color 0.22s ease;
        }}
        .tactile-card:hover {{
            transform: translateY(-2px);
            box-shadow: 0 16px 36px -8px rgba(15, 23, 42, 0.08), 0 4px 12px -2px rgba(15, 23, 42, 0.04);
        }}
        .tactile-card:active {{
            transform: scale(0.99);
        }}

        /* Ripple Animation */
        .el-ripple {{
            position: absolute;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.45);
            transform: scale(0);
            animation: rippleAnim 0.6s linear;
            pointer-events: none;
        }}
        @keyframes rippleAnim {{
            to {{
                transform: scale(3.5);
                opacity: 0;
            }}
        }}

        /* Number Update Flash */
        @keyframes valuePulse {{
            0% {{ transform: scale(1); }}
            50% {{ transform: scale(1.03); color: #1464F4; }}
            100% {{ transform: scale(1); }}
        }}
        .value-updated-pulse {{
            animation: valuePulse 0.3s ease-out;
        }}

        /* Elementor Studio Console Cards */
        .el-console-card {{
            background: #FFFFFF;
            border: 1px solid rgba(226, 232, 240, 0.9);
            border-radius: 1.25rem;
            box-shadow: 0 4px 20px -2px rgba(15, 23, 42, 0.05);
            overflow: hidden;
            position: relative;
            transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1);
        }}
        .el-console-card:hover {{
            border-color: rgba(147, 197, 253, 0.7);
            box-shadow: 0 12px 30px -4px rgba(20, 100, 244, 0.08);
        }}
        .el-console-header {{
            background: linear-gradient(135deg, #1464F4 0%, #1D4ED8 100%);
            color: #FFFFFF;
            padding: 1rem 1.25rem;
            position: relative;
        }}
        .el-console-header-purple {{
            background: linear-gradient(135deg, #7C3AED 0%, #6D28D9 100%);
        }}

        /* Swatch Chips with 3D tactile feel */
        .el-color-swatch {{
            position: relative;
            width: 36px;
            height: 36px;
            border-radius: 10px;
            cursor: pointer;
            display: inline-block;
            border: 2px solid #ffffff;
            box-shadow: 0 2px 5px rgba(0, 0, 0, 0.15), 0 0 0 1px rgba(0, 0, 0, 0.1);
            transition: all 0.2s cubic-bezier(0.34, 1.56, 0.64, 1);
            outline: none;
            flex-shrink: 0;
        }}
        .el-color-swatch:hover {{
            transform: translateY(-2px) scale(1.15);
            box-shadow: 0 8px 16px -2px rgba(20, 100, 244, 0.35), 0 0 0 2px #1464F4;
            z-index: 2;
        }}
        .el-color-swatch:active {{
            transform: scale(0.92);
        }}
        .el-color-swatch.is-active {{
            transform: scale(1.12);
            box-shadow: 0 0 0 2.5px #ffffff, 0 0 0 4.5px #1464F4, 0 8px 18px -2px rgba(20, 100, 244, 0.42);
            z-index: 3;
        }}
        .el-color-swatch.is-active::after {{
            content: '✓';
            position: absolute;
            inset: 0;
            display: flex;
            align-items: center;
            justify-content: center;
            color: #ffffff;
            font-size: 13px;
            font-weight: 900;
            text-shadow: 0 1px 3px rgba(0,0,0,0.8), 0 0 2px rgba(0,0,0,0.9);
        }}

        /* Showroom Car Stage Lighting */
        .car-stage-bg {{
            background: radial-gradient(ellipse at 50% 65%, rgba(20, 100, 244, 0.12) 0%, rgba(241, 245, 249, 0.7) 50%, #f8fafc 100%);
            position: relative;
            perspective: 800px;
        }}
        .car-stage-bg::after {{
            content: '';
            position: absolute;
            bottom: 12px;
            left: 12%;
            right: 12%;
            height: 18px;
            background: radial-gradient(ellipse at 50% 50%, rgba(15, 23, 42, 0.16) 0%, transparent 70%);
            pointer-events: none;
        }}
        #quote-car-img {{
            transition: transform 0.35s cubic-bezier(0.16, 1, 0.3, 1), filter 0.35s ease;
            transform: rotateX(var(--rx, 0deg)) rotateY(var(--ry, 0deg));
        }}

        /* ================= KHÓA CỨNG KÍCH THƯỚC BÁO GIÁ ĐỂ XUẤT ẢNH LUÔN NÉT 1024PX ================= */
        #capture-area {{
            box-sizing: border-box;
            width: 1024px;
            min-width: 1024px;
            max-width: 1024px;
            background: white;
            box-shadow: 0 10px 35px -5px rgba(0, 0, 0, 0.08);
            overflow: hidden;
            border-radius: 16px;
        }}
        #capture-area, #capture-area * {{ box-sizing: border-box; }}

        .capture-grid-main {{
            display: grid;
            grid-template-columns: minmax(0, 54fr) minmax(410px, 46fr);
            gap: 18px;
            align-items: start;
        }}
        .quote-intro-card {{ min-width: 0; }}
        .quote-price-card {{
            background: linear-gradient(180deg, #f8fafc 0%, #ffffff 100%);
            border: 1px solid #dfe6ef;
            border-radius: 14px;
            padding: 17px 18px;
            box-shadow: 0 4px 14px rgba(15, 23, 42, 0.04);
            min-width: 0;
        }}
        .quote-price-row {{
            display: grid;
            grid-template-columns: max-content minmax(18px, 1fr) max-content;
            align-items: center;
            gap: 8px;
            min-height: 33px;
            font-size: 15px;
            line-height: 1.25;
        }}
        .quote-price-row .dot-leader {{ margin: 0 !important; min-width: 14px; }}
        .quote-price-row > span:first-child {{ min-width: 0; }}
        .quote-price-row > span:last-child {{
            white-space: nowrap;
            text-align: right;
            font-size: 16px;
            line-height: 1.15;
            letter-spacing: -0.01em;
            font-family: 'JetBrains Mono', monospace;
        }}
        .quote-price-final-row {{
            margin-top: 11px;
            padding-top: 13px;
            border-top: 1px solid #dbe4ef;
            grid-template-columns: max-content minmax(12px, 1fr) max-content;
        }}
        .quote-price-final-row > span:first-child {{
            font-size: 13px !important;
            line-height: 1.2;
            white-space: nowrap;
        }}
        .quote-price-final-row #quote-price-final {{
            font-size: 27px;
            line-height: 1;
            white-space: nowrap;
            letter-spacing: -0.025em;
            font-family: 'JetBrains Mono', monospace;
        }}
        .quote-primary-row {{
            display: grid !important;
            grid-template-columns: minmax(0, 1.45fr) minmax(0, .85fr);
            gap: 8px !important;
            margin-top: 10px !important;
        }}
        .quote-primary-row > div {{
            width: auto !important;
            min-width: 0;
            height: 42px !important;
            padding-left: 11px !important;
            padding-right: 10px !important;
        }}
        .quote-option-grid {{
            display: grid;
            grid-template-columns: repeat(4, minmax(0, 1fr));
            gap: 7px;
            margin-top: 8px;
        }}
        .quote-fee-option-grid {{
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 7px;
            margin-top: 7px;
        }}
        .quote-option {{
            min-width: 0;
            height: 42px;
            border-radius: 8px;
            padding: 0 9px;
            display: flex;
            align-items: center;
            background: #f3f4f6;
        }}
        .quote-fee-option-grid .quote-option {{
            background: #eff6ff;
            border: 1px solid #dbeafe;
        }}
        .quote-fee-option-grid .quote-option label {{ color: #1d4ed8; }}
        .quote-option label {{
            min-width: auto;
            margin-right: 6px;
            font-size: 10px;
            font-weight: 700;
            color: #6b7280;
            white-space: nowrap;
        }}
        .quote-option select {{
            min-width: 0;
            flex: 1;
            font-size: 11px;
            font-weight: 700;
            color: #374151;
            background: transparent;
            outline: none;
        }}
        .color-option-wrap {{
            height: auto !important;
            min-height: 42px;
            display: block !important;
            padding: 0 !important;
            overflow: visible;
        }}
        .color-option-main {{
            min-height: 42px !important;
            padding: 0 9px !important;
            display: flex;
            align-items: center;
            width: 100%;
        }}
        .color-option-main select {{ height: 42px !important; }}
        .color-surcharge-hint {{
            padding: 3px 9px 5px !important;
            font-size: 9px !important;
            line-height: 1.2 !important;
            font-weight: 900;
            color: #b45309;
            background: #fffbeb;
            border-top: 1px solid #fde68a;
            border-radius: 0 0 6px 6px;
        }}

        .capture-grid-cost {{
            display: grid;
            grid-template-columns: minmax(0, 42fr) minmax(0, 58fr);
            gap: 28px;
            align-items: stretch;
        }}
        .capture-col {{ min-width: 0; }}
        #quote-promo-list {{
            display: grid !important;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 10px;
            width: 100%;
            min-width: 0;
        }}
        #quote-promo-list > li {{ width: auto !important; min-width: 0; }}
        .dot-leader {{
            flex: 1;
            border-bottom: 1px dotted #cbd5e1;
            margin: 0 10px;
            position: relative;
            top: -4px;
        }}
        select {{ -webkit-appearance: none; -moz-appearance: none; appearance: none; background-color: transparent; outline: none; }}

        /* Modals */
        .modal-backdrop-blur {{
            background: rgba(15, 23, 42, 0.75);
            backdrop-filter: blur(8px);
            -webkit-backdrop-filter: blur(8px);
        }}
        .modal-content-box {{
            border-radius: 1.25rem;
            box-shadow: 0 25px 60px -15px rgba(0, 0, 0, 0.35);
            border: 1px solid rgba(255, 255, 255, 0.15);
            animation: modalScaleIn 0.22s cubic-bezier(0.16, 1, 0.3, 1);
        }}
        @keyframes modalScaleIn {{
            from {{ opacity: 0; transform: scale(0.96) translateY(8px); }}
            to {{ opacity: 1; transform: scale(1) translateY(0); }}
        }}

        /* Custom Scrollbars */
        ::-webkit-scrollbar {{ width: 6px; height: 6px; }}
        ::-webkit-scrollbar-thumb {{ background: #cbd5e1; border-radius: 4px; }}
        ::-webkit-scrollbar-thumb:hover {{ background: #94a3b8; }}
        .hide-scroll::-webkit-scrollbar {{ display: none; }}
        .hide-scroll {{ -ms-overflow-style: none; scrollbar-width: none; }}

        /* ================= MAGIC CYBER-MODAL: TUỲ CHỈNH BIỂU PHÍ & LĂN BÁNH ================= */
        #live-customize-backdrop {{
            position: fixed;
            inset: 0;
            background: rgba(15, 23, 42, 0.75);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
            z-index: 998;
            transition: opacity 0.3s ease;
        }}
        #live-customize-backdrop.hidden {{ display: none; }}

        #live-customize-panel {{
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) scale(1);
            z-index: 999;
            width: 720px;
            max-width: calc(100vw - 28px);
            max-height: calc(100vh - 40px);
            overflow-y: auto;
            background: #FFFFFF;
            border: 1px solid rgba(147, 51, 234, 0.35);
            border-radius: 28px;
            box-shadow: 0 25px 70px -10px rgba(124, 58, 237, 0.35), 0 0 0 1px rgba(255,255,255,0.8) inset;
            padding: 0;
            transition: all 0.28s cubic-bezier(0.34, 1.56, 0.64, 1);
        }}
        #live-customize-panel.hidden-panel {{
            display: none;
            opacity: 0;
            transform: translate(-50%, -46%) scale(0.96);
        }}
        #live-customize-panel .live-modal-header {{
            background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #2e1065 100%);
            color: #ffffff;
            padding: 20px 24px;
            border-top-left-radius: 27px;
            border-top-right-radius: 27px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid rgba(192, 132, 252, 0.25);
            position: relative;
        }}
        #live-customize-panel .live-modal-header::after {{
            content: '';
            position: absolute;
            bottom: 0;
            left: 0;
            right: 0;
            height: 2px;
            background: linear-gradient(90deg, #38bdf8, #a855f7, #ec4899);
        }}
        #live-customize-panel .live-close {{
            border: 1px solid rgba(255,255,255,0.2);
            background: rgba(255,255,255,0.1);
            color: #ffffff;
            width: 36px;
            height: 36px;
            border-radius: 12px;
            font-size: 20px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.2s ease;
        }}
        #live-customize-panel .live-close:hover {{
            background: rgba(239, 68, 68, 0.85);
            transform: scale(1.08) rotate(90deg);
        }}
        #live-customize-panel .live-modal-body {{
            padding: 24px;
        }}
        #live-customize-panel .live-grid {{ display: grid; grid-template-columns: 1fr; gap: 14px; }}
        #live-customize-panel .live-fee-row {{ display: grid; grid-template-columns: minmax(0, 1.4fr) minmax(180px, .8fr); gap: 12px; }}
        #live-customize-panel .live-field {{
            min-width: 0;
            background: #F8FAFC;
            border: 1.5px solid #E2E8F0;
            border-radius: 16px;
            padding: 12px 14px;
            transition: all 0.2s ease;
        }}
        #live-customize-panel .live-field:focus-within {{
            background: #FFFFFF;
            border-color: #9333EA;
            box-shadow: 0 0 0 3px rgba(147, 51, 234, 0.15);
        }}
        #live-customize-panel .live-field label {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            font-size: 12px;
            font-weight: 800;
            color: #334155;
            margin-bottom: 8px;
        }}
        #live-customize-panel .live-field input,
        #live-customize-panel .live-field select {{
            width: 100%;
            height: 42px;
            border: 1.5px solid #CBD5E1;
            border-radius: 10px;
            padding: 0 12px;
            font-size: 14px;
            font-weight: 800;
            text-align: right;
            outline: none;
            background: #FFFFFF;
            transition: all 0.2s ease;
        }}
        #live-customize-panel .live-field select {{ text-align: left; font-weight: 700; }}
        #live-customize-panel .live-field input:focus,
        #live-customize-panel .live-field select:focus {{
            border-color: #9333EA;
        }}
        #live-customize-panel .live-section-title {{
            font-size: 12.5px;
            font-weight: 900;
            color: #6B21A8;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            display: flex;
            align-items: center;
            gap: 8px;
            padding-top: 10px;
            margin-top: 4px;
            border-top: 1px dashed #E2E8F0;
        }}
        #live-customize-panel .live-section-title:first-child {{ border-top: 0; padding-top: 0; }}
        #live-customize-panel .live-help {{ margin-top: 6px; font-size: 11px; line-height: 1.4; color: #64748B; }}

        /* Laser Beam Traveling Animation */
        @keyframes laserRun {{
            0% {{ background-position: -200% 0; }}
            100% {{ background-position: 200% 0; }}
        }}
        .nav-laser-beam {{
            height: 2px;
            width: 100%;
            background: linear-gradient(90deg, transparent 0%, #38bdf8 30%, #818cf8 50%, #c084fc 70%, transparent 100%);
            background-size: 200% 100%;
            animation: laserRun 6s linear infinite;
        }}

        /* Holographic Cyber Pedestal */
        .cyber-pedestal-rings {{
            position: absolute;
            bottom: 6px;
            left: 50%;
            transform: translateX(-50%) rotateX(75deg);
            width: 380px;
            height: 160px;
            border-radius: 50%;
            border: 2px dashed rgba(56, 189, 248, 0.45);
            box-shadow: 0 0 25px rgba(56, 189, 248, 0.35), inset 0 0 20px rgba(56, 189, 248, 0.25);
            pointer-events: none;
            animation: pedestalPulse 4s ease-in-out infinite alternate;
        }}
        .cyber-pedestal-rings::before {{
            content: '';
            position: absolute;
            inset: 15px;
            border-radius: 50%;
            border: 1px solid rgba(168, 85, 247, 0.5);
            box-shadow: 0 0 15px rgba(168, 85, 247, 0.3);
        }}
        @keyframes pedestalPulse {{
            0% {{ transform: translateX(-50%) rotateX(75deg) scale(0.96); opacity: 0.6; }}
            100% {{ transform: translateX(-50%) rotateX(75deg) scale(1.04); opacity: 1; }}
        }}

        /* Color Swatch Halo Pulse */
        @keyframes swatchGlow {{
            0%, 100% {{ box-shadow: 0 0 0 2.5px #ffffff, 0 0 0 4.5px #1464F4, 0 8px 18px -2px rgba(20, 100, 244, 0.42); }}
            50% {{ box-shadow: 0 0 0 2.5px #ffffff, 0 0 0 5.5px #06B6D4, 0 12px 24px -2px rgba(6, 182, 212, 0.6); }}
        }}
        .el-color-swatch.is-active {{
            animation: swatchGlow 2.5s ease-in-out infinite;
        }}

        /* Responsive Mobile Styles */
        @media (max-width: 767px) {{
            body {{ padding-bottom: calc(75px + env(safe-area-inset-bottom)); }}
            #capture-area {{
                width: 100% !important; min-width: 0 !important; max-width: 100% !important;
                border-radius: 14px;
            }}
            #capture-area header {{ padding: 14px !important; }}
            #capture-area > header + div {{ padding: 14px !important; }}
            #capture-area .capture-grid-main, #capture-area .capture-grid-cost {{
                grid-template-columns: 1fr !important;
                gap: 12px !important;
            }}
            #capture-area .quote-spec-card > .grid:first-child {{
                grid-template-columns: 1fr !important;
            }}
            #capture-area #quote-promo-list {{
                grid-template-columns: 1fr !important;
            }}
            #capture-area .quote-price-card {{ padding: 14px !important; }}
            #capture-area .quote-option-grid {{ grid-template-columns: repeat(2, 1fr) !important; }}
            #capture-area .quote-fee-option-grid {{ grid-template-columns: 1fr !important; }}
        }}

        /* V74: Export clone cố định desktop 1024px - KHÔNG dùng layout mobile */
        #temporary-export-root,
        #temporary-pdf-export-root,
        #capture-area-clone.export-desktop-clone {{
            transform: none !important;
            zoom: 1 !important;
        }}
        #capture-area-clone.export-desktop-clone {{
            display: block !important;
            width: 1024px !important;
            min-width: 1024px !important;
            max-width: 1024px !important;
            background: #fff !important;
            font-size: 16px !important;
            line-height: normal !important;
            overflow: visible !important;
        }}
        #capture-area-clone.export-desktop-clone img {{
            object-fit: contain !important;
        }}
        #capture-area-clone.export-desktop-clone header {{
            display: flex !important;
            justify-content: space-between !important;
            align-items: center !important;
            padding: 24px 28px !important;
            border-bottom: 4px solid #1464f4 !important;
            min-height: 90px !important;
        }}
        #capture-area-clone.export-desktop-clone header > div:first-child {{
            flex: 1 1 auto !important;
            min-width: 0 !important;
            max-width: none !important;
        }}
        #capture-area-clone.export-desktop-clone header h1 {{
            font-size: 24px !important;
            line-height: 30px !important;
            margin: 0 0 4px 0 !important;
            white-space: nowrap !important;
        }}
        #capture-area-clone.export-desktop-clone header p {{
            font-size: 13px !important;
            line-height: 20px !important;
            margin: 0 !important;
            white-space: nowrap !important;
        }}
        #capture-area-clone.export-desktop-clone .capture-grid-main {{
            display: grid !important;
            grid-template-columns: minmax(0, 54fr) minmax(410px, 46fr) !important;
            gap: 18px !important;
            align-items: start !important;
        }}
        #capture-area-clone.export-desktop-clone .quote-price-card {{
            min-width: 0 !important;
            padding: 16px 20px !important;
        }}
        #capture-area-clone.export-desktop-clone .quote-price-row {{
            min-height: 36px !important;
            height: auto !important;
            font-size: 14.5px !important;
            line-height: 20px !important;
            display: flex !important;
            justify-content: space-between !important;
            align-items: center !important;
            margin-bottom: 4px !important;
        }}
        #capture-area-clone.export-desktop-clone .quote-price-row > span:first-child {{
            white-space: nowrap !important;
            font-size: 14.5px !important;
        }}
        #capture-area-clone.export-desktop-clone .quote-price-row > span:last-child {{
            font-size: 16px !important;
            white-space: nowrap !important;
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace !important;
        }}
        #capture-area-clone.export-desktop-clone .quote-price-final-row {{
            margin-top: 8px !important;
            padding-top: 8px !important;
        }}
        #capture-area-clone.export-desktop-clone .quote-price-final-row #quote-price-final {{
            font-size: 26px !important;
            line-height: 32px !important;
            white-space: nowrap !important;
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace !important;
        }}
        #capture-area-clone.export-desktop-clone .capture-grid-cost {{
            display: grid !important;
            grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
            gap: 18px !important;
            align-items: stretch !important;
        }}
        #capture-area-clone.export-desktop-clone .quote-option-grid {{
            display: grid !important;
            grid-template-columns: repeat(4, minmax(0, 1fr)) !important;
            gap: 8px !important;
        }}
        #capture-area-clone.export-desktop-clone .quote-fee-option-grid {{
            display: grid !important;
            grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
            gap: 8px !important;
        }}
        #capture-area-clone.export-desktop-clone #quote-promo-list {{
            display: grid !important;
            grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
            gap: 10px !important;
        }}
        #capture-area-clone.export-desktop-clone #warranty-panel,
        #capture-area-clone.export-desktop-clone #charging-promo-panel {{
            overflow: visible !important;
        }}
        #capture-area-clone.export-desktop-clone #warranty-panel h3,
        #capture-area-clone.export-desktop-clone #charging-promo-panel h3 {{
            font-size: 15px !important;
            line-height: 22px !important;
            margin: 0 0 2px 0 !important;
            white-space: nowrap !important;
        }}
        #capture-area-clone.export-desktop-clone #warranty-subtitle {{
            font-size: 12px !important;
            line-height: 18px !important;
            margin: 0 !important;
            white-space: nowrap !important;
        }}
        #capture-area-clone.export-desktop-clone .quote-spec-card {{
            display: block !important;
            width: 100% !important;
            overflow: hidden !important;
        }}
        #capture-area-clone.export-desktop-clone .quote-spec-card > .grid:first-child {{
            display: grid !important;
            grid-template-columns: minmax(0, 1.65fr) minmax(330px, 1fr) !important;
            min-height: 390px !important;
            width: 100% !important;
            align-items: stretch !important;
        }}
        #capture-area-clone.export-desktop-clone .quote-spec-card > .grid:first-child > div:first-child {{
            min-width: 0 !important;
            min-height: 390px !important;
            padding: 16px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            border-right: 1px solid #f3f4f6 !important;
            border-bottom: 0 !important;
        }}
        #capture-area-clone.export-desktop-clone .quote-spec-card > .grid:first-child > div:nth-child(2) {{
            min-width: 0 !important;
            padding: 16px 20px !important;
            border-left: 0 !important;
            border-top: 0 !important;
        }}
        #capture-area-clone.export-desktop-clone #quote-selected-color {{
            font-size: 13px !important;
            font-weight: 700 !important;
            color: #1e40af !important;
        }}
        #capture-area-clone.export-desktop-clone .el-color-swatch {{
            width: 32px !important;
            height: 32px !important;
            border-radius: 8px !important;
            display: inline-block !important;
            border: 2px solid #ffffff !important;
            box-shadow: 0 1px 4px rgba(0,0,0,0.2) !important;
            flex-shrink: 0 !important;
        }}
        #capture-area-clone.export-desktop-clone .el-color-swatch.is-active {{
            box-shadow: 0 0 0 2px #ffffff, 0 0 0 3.5px #1464f4 !important;
        }}
        #capture-area-clone.export-desktop-clone #quote-car-img {{
            display: block !important;
            width: auto !important;
            height: auto !important;
            max-width: 96% !important;
            max-height: 340px !important;
            margin: auto !important;
        }}
        #capture-area-clone.export-desktop-clone #quote-car-specs {{
            display: block !important;
            max-height: none !important;
            height: auto !important;
            overflow: visible !important;
            padding-right: 0 !important;
        }}
        #capture-area-clone.export-desktop-clone #quote-car-specs li {{
            width: 100% !important;
            font-size: 11px !important;
            line-height: 15px !important;
            margin-bottom: 5px !important;
        }}
        #capture-area-clone.export-desktop-clone .quote-spec-card > .grid:nth-child(2) {{
            display: grid !important;
            grid-template-columns: repeat(3, minmax(0, 1fr)) !important;
            width: 100% !important;
            border-top: 1px solid #e5e7eb !important;
        }}
        #capture-area-clone.export-desktop-clone .quote-spec-card > .grid:nth-child(2) > div {{
            width: auto !important;
            min-width: 0 !important;
            padding: 15px 10px !important;
            text-align: center !important;
        }}
        #capture-area-clone.export-desktop-clone .quote-total-footer {{
            display: flex !important;
            flex-direction: row !important;
            justify-content: space-between !important;
            align-items: center !important;
            padding: 22px 28px !important;
            background: #1d4ed8 !important;
            background: linear-gradient(135deg, #1e3a8a 0%, #2563eb 50%, #1e40af 100%) !important;
            border-bottom: 8px solid #1464f4 !important;
        }}
        #capture-area-clone.export-desktop-clone .quote-total-footer h2 {{
            font-size: 26px !important;
            line-height: 34px !important;
            margin: 0 0 4px 0 !important;
            display: block !important;
            white-space: nowrap !important;
            color: #ffffff !important;
            font-weight: 900 !important;
        }}
        #capture-area-clone.export-desktop-clone .quote-total-footer p {{
            font-size: 13px !important;
            line-height: 20px !important;
            margin: 0 !important;
            display: block !important;
            color: #dbeafe !important;
            white-space: nowrap !important;
            font-weight: 600 !important;
        }}
        #capture-area-clone.export-desktop-clone #quote-total {{
            font-size: 42px !important;
            line-height: 48px !important;
            padding: 12px 26px !important;
            white-space: nowrap !important;
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace !important;
            font-weight: 900 !important;
            color: #1464f4 !important;
            background: #ffffff !important;
            border-radius: 16px !important;
        }}
        #capture-area-clone.export-focus-clone {{
            box-shadow: none !important;
            border-radius: 0 !important;
        }}
    </style>
</head>
<body class="antialiased text-gray-800 relative bg-slate-100">

    <!-- Ambient Aurora Background Orbs -->
    <div class="aurora-bg-wrap">
        <div class="aurora-orb aurora-orb-1"></div>
        <div class="aurora-orb aurora-orb-2"></div>
        <div class="aurora-orb aurora-orb-3"></div>
    </div>

    <!-- ================= TOP CYBER-LUXURY STUDIO NAVIGATION BAR ================= -->
    <nav id="top-command-bar" class="sticky top-0 z-40 w-full px-4 xl:px-8 py-2.5 text-white bg-slate-900/90 backdrop-blur-xl border-b border-slate-700/60 shadow-lg">
        <div class="max-w-[1560px] mx-auto flex flex-wrap items-center justify-between gap-3">
            <!-- Brand & Status -->
            <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-2xl bg-gradient-to-br from-blue-500 via-blue-600 to-cyan-400 flex items-center justify-center shadow-lg shadow-blue-500/35 font-display font-black text-lg tracking-tighter text-white ring-2 ring-blue-400/30">
                    VF
                </div>
                <div>
                    <div class="flex items-center gap-2">
                        <span class="font-display font-extrabold text-base sm:text-lg tracking-tight text-white">VINFAST THẾ TÀI</span>
                        <span class="hidden sm:inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-black uppercase tracking-wider bg-gradient-to-r from-blue-500 to-cyan-400 text-slate-950">STUDIO 2026</span>
                    </div>
                    <div class="flex items-center gap-2 mt-0.5">
                        <span id="online-status" class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-[10px] font-bold bg-slate-800 border border-slate-700 text-emerald-400">
                            <span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                            Online: Sẵn sàng
                        </span>
                        <span class="text-[11px] text-slate-400 hidden md:inline">• Hotline: 0772 993 837</span>
                    </div>
                </div>
            </div>

            <!-- Current Model Quick Pill -->
            <div id="quick-car-badge" class="hidden md:flex items-center gap-2 px-3.5 py-1.5 rounded-xl bg-slate-800/90 border border-slate-700/80 text-xs">
                <span class="text-white font-black">VINFAST</span>
                <span class="text-cyan-400 font-bold">• Đang tải...</span>
            </div>

            <!-- Global Action Tools (Tactile Buttons) -->
            <div class="flex items-center gap-2 flex-wrap">
                <!-- Group 1: Output Actions -->
                <button type="button" onclick="openPreview()" class="tactile-btn px-4 py-2 rounded-xl bg-gradient-to-r from-blue-600 via-blue-500 to-cyan-500 hover:from-blue-500 hover:to-cyan-400 text-white text-xs sm:text-sm font-black shadow-lg shadow-blue-500/30 flex items-center gap-1.5 border border-cyan-300/30">
                    <span>📸</span><span>Lưu Hình HD</span>
                </button>
                <button type="button" onclick="savePreviewPdf('full', this)" class="tactile-btn px-3 py-2 rounded-xl bg-rose-600 hover:bg-rose-500 text-white text-xs sm:text-sm font-black shadow-lg shadow-rose-600/25 flex items-center gap-1 border border-rose-400/30">
                    <span>📄</span><span class="hidden sm:inline">Xuất PDF</span>
                </button>
                <button type="button" onclick="openQuoteInfo()" class="tactile-btn px-3 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs sm:text-sm font-black shadow-lg shadow-emerald-600/25 flex items-center gap-1 border border-emerald-400/30">
                    <span>📋</span><span>Copy Text</span>
                </button>

                <!-- Group 2: Modals & Settings -->
                <button type="button" onclick="toggleLiveCustomize(true)" class="tactile-btn px-3 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-white text-xs sm:text-sm font-black shadow-lg shadow-purple-600/25 flex items-center gap-1 border border-purple-400/30">
                    <span>⚙</span><span>Phí & Bank</span>
                </button>

                <!-- Group 3: Data Management -->
                <div class="hidden lg:flex items-center gap-1 bg-slate-800/90 p-1 rounded-xl border border-slate-700/80">
                    <button type="button" onclick="openCarManager()" class="tactile-btn px-2.5 py-1.5 rounded-lg hover:bg-slate-700 text-[11px] font-bold text-slate-200" title="Quản lý dữ liệu xe">
                        🚗 Xe
                    </button>
                    <button type="button" onclick="openPromoManager()" class="tactile-btn px-2.5 py-1.5 rounded-lg hover:bg-slate-700 text-[11px] font-bold text-slate-200" title="Quản lý CTKM">
                        🎯 CTKM
                    </button>
                    <button type="button" onclick="openAccManager()" class="tactile-btn px-2.5 py-1.5 rounded-lg hover:bg-slate-700 text-[11px] font-bold text-slate-200" title="Quản lý phụ kiện">
                        📦 Phụ Kiện
                    </button>
                    <button type="button" onclick="openComboPicker()" class="tactile-btn px-2.5 py-1.5 rounded-lg hover:bg-slate-700 text-[11px] font-bold text-slate-200" title="Quà tặng combo">
                        🎁 Combo
                    </button>
                </div>

                <!-- Group 4: Cloud & Data Sync -->
                <div class="hidden xl:flex items-center gap-1 bg-slate-800/90 p-1 rounded-xl border border-slate-700/80">
                    <button type="button" id="sync-online-btn" onclick="syncDataFromSupabase(true)" class="tactile-btn px-2 py-1.5 rounded-lg hover:bg-slate-700 text-[11px] font-bold text-cyan-400" title="Đồng bộ dữ liệu Supabase">
                        ↻ Sync
                    </button>
                    <button type="button" id="save-online-btn" onclick="saveDataToSupabase()" class="tactile-btn px-2 py-1.5 rounded-lg hover:bg-slate-700 text-[11px] font-bold text-emerald-400" title="Lưu lên Cloud Supabase">
                        ☁ Lưu
                    </button>
                    <button type="button" onclick="exportAllDataToFile()" class="tactile-btn px-2 py-1.5 rounded-lg hover:bg-slate-700 text-[11px] font-bold text-slate-300" title="Tải file JSON backup">
                        ⬇ File
                    </button>
                    <label class="tactile-btn px-2 py-1.5 rounded-lg hover:bg-slate-700 text-[11px] font-bold text-slate-300 cursor-pointer mb-0" title="Nhập file JSON">
                        ⬆ File<input type="file" class="hidden" accept=".json" onchange="importAllDataFromFile(event)">
                    </label>
                </div>
            </div>
        </div>
    </nav>
    <div class="nav-laser-beam"></div>

    <!-- ================= MAGIC CYBER-MODAL: BẢNG TÙY CHỈNH BIỂU PHÍ & LĂN BÁNH ================= -->
    <input type="checkbox" id="customize-toggle" class="hidden" onchange="toggleLiveCustomize(this.checked)">
    <div id="live-customize-backdrop" class="hidden" onclick="toggleLiveCustomize(false)"></div>
    <div id="live-customize-panel" class="hidden-panel">
        <div class="live-modal-header">
            <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-xl bg-purple-500/20 border border-purple-400/40 flex items-center justify-center text-purple-300 shadow-inner">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"/><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/></svg>
                </div>
                <div>
                    <div class="font-extrabold text-base text-white flex items-center gap-2">
                        <span>TÙY CHỈNH BIỂU PHÍ & LĂN BÁNH</span>
                        <span class="text-[10px] font-black uppercase px-2 py-0.5 rounded-full bg-purple-500/30 text-purple-300 border border-purple-400/30">Magic Editor</span>
                    </div>
                    <div class="text-xs font-semibold text-purple-200 mt-0.5 flex items-center gap-2">
                        <span id="live-customize-car">Xe đang chọn</span>
                        <span class="text-slate-400">• Tự động áp dụng giá lăn bánh tức thì</span>
                    </div>
                </div>
            </div>
            <button type="button" class="live-close" onclick="toggleLiveCustomize(false)" title="Đóng bảng">&times;</button>
        </div>

        <div class="live-modal-body">
            <div class="live-grid">
                <!-- Group 1: Registration Fees -->
                <div class="live-section-title">
                    <svg class="w-4 h-4 text-purple-600" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M4 4a2 2 0 012-2h8a2 2 0 012 2v12a1 1 0 110 2h-3a1 1 0 01-1-1v-2a1 1 0 00-1-1H9a1 1 0 00-1 1v2a1 1 0 01-1 1H4a1 1 0 110-2V4zm3 1h2v2H7V5zm2 4H7v2h2V9zm2-4h2v2h-2V5zm2 4h-2v2h2V9z" clip-rule="evenodd"/></svg>
                    <span>Chi Phí Đăng Ký Xe & Lăn Bánh Bắt Buộc</span>
                </div>

                <div class="live-fee-row">
                    <div class="live-field">
                        <label>
                            <span>Khu vực đăng ký (Biển số)</span>
                            <span class="text-[10px] text-purple-600 font-bold uppercase">Mức chuẩn</span>
                        </label>
                        <select id="live-registration-preset" onchange="applyRegistrationPreset()">
                            <option value="ward">Phường / Xã — 140.000 VNĐ</option>
                            <option value="metro">TP. HCM / Hà Nội — 14.000.000 VNĐ</option>
                            <option value="custom">Tùy chỉnh số tiền nhập tay</option>
                        </select>
                    </div>
                    <div class="live-field">
                        <label><span>Lệ phí đăng ký</span><span class="text-[10px] text-slate-400">VNĐ</span></label>
                        <input type="text" id="live-registration-fee" autocomplete="off">
                    </div>
                </div>

                <div class="live-fee-row">
                    <div class="live-field">
                        <label><span>Loại đăng kiểm xe</span><span class="text-[10px] text-purple-600 font-bold uppercase">Mức chuẩn</span></label>
                        <select id="live-inspection-preset" onchange="applyInspectionPreset()">
                            <option value="57">Xe 5/7 chỗ — 90.000 VNĐ</option>
                            <option value="custom">Tùy chỉnh số tiền</option>
                        </select>
                    </div>
                    <div class="live-field">
                        <label><span>Phí đăng kiểm</span><span class="text-[10px] text-slate-400">VNĐ</span></label>
                        <input type="text" id="live-inspection-fee" autocomplete="off">
                    </div>
                </div>

                <div class="live-fee-row">
                    <div class="live-field">
                        <label><span>Bảo hiểm trách nhiệm dân sự (TNDS)</span><span class="text-[10px] text-purple-600 font-bold uppercase">Mức chuẩn</span></label>
                        <select id="live-civil-preset" onchange="applyCivilPreset()">
                            <option value="family4">Gia đình 4 chỗ / Biển trắng — 520.700 VNĐ</option>
                            <option value="family5">Gia đình 5 chỗ / Biển trắng — 530.700 VNĐ</option>
                            <option value="family7">Gia đình 7 chỗ / Biển trắng — 1.013.400 VNĐ</option>
                            <option value="taxi5">Taxi 5 chỗ / Biển vàng — 1.443.720 VNĐ</option>
                            <option value="taxi7">Taxi 7 chỗ / Biển vàng — 2.049.600 VNĐ</option>
                            <option value="business5">KD UDCN 5 chỗ / Biển vàng — 861.600 VNĐ</option>
                            <option value="business7">KD UDCN 7 chỗ / Biển vàng — 1.218.000 VNĐ</option>
                            <option value="custom">Tùy chỉnh số tiền</option>
                        </select>
                        <div class="live-help">Đã tính trọn gói bảo hiểm tai nạn lái phụ xe theo mức chọn.</div>
                    </div>
                    <div class="live-field">
                        <label><span>Bảo hiểm dân sự</span><span class="text-[10px] text-slate-400">VNĐ</span></label>
                        <input type="text" id="live-civil-fee" autocomplete="off">
                    </div>
                </div>

                <div class="live-fee-row">
                    <div class="live-field">
                        <label><span>Phí bảo trì đường bộ</span><span class="text-[10px] text-purple-600 font-bold uppercase">Mức chuẩn</span></label>
                        <select id="live-road-preset" onchange="applyRoadPreset()">
                            <option value="white1">Biển trắng — 1 năm — 1.560.000 VNĐ</option>
                            <option value="white3">Biển trắng — 3 năm — 4.325.000 VNĐ</option>
                            <option value="yellow1">Biển vàng / EC VAN / Bán tải — 1 năm — 2.160.000 VNĐ</option>
                            <option value="custom">Tùy chỉnh số tiền</option>
                        </select>
                    </div>
                    <div class="live-field">
                        <label><span>Phí đường bộ</span><span class="text-[10px] text-slate-400">VNĐ</span></label>
                        <input type="text" id="live-road-fee" autocomplete="off">
                    </div>
                </div>

                <!-- Group 2: BHVC & Registration Service -->
                <div class="live-section-title">
                    <svg class="w-4 h-4 text-purple-600" fill="currentColor" viewBox="0 0 20 20"><path fill-rule="evenodd" d="M10 1.944A11.954 11.954 0 012.166 5C2.056 5.649 2 6.319 2 7c0 5.225 3.34 9.67 8 11.317C14.66 16.67 18 12.225 18 7c0-.682-.057-1.35-.166-2.001A11.954 11.954 0 0110 1.944zM11 14a1 1 0 11-2 0 1 1 0 012 0zm0-7a1 1 0 10-2 0v3a1 1 0 102 0V7z" clip-rule="evenodd"/></svg>
                    <span>Dịch Vụ Đăng Ký & Bảo Hiểm Vật Chất (BHVC)</span>
                </div>

                <div class="live-fee-row">
                    <div class="live-field">
                        <label><span>Dịch vụ đăng ký trọn gói</span><span class="text-[10px] text-slate-400">Đại lý</span></label>
                        <input type="text" id="live-registration-service" autocomplete="off" placeholder="VD: 3.000.000">
                    </div>
                    <div class="live-field">
                        <label><span>Tỷ lệ Bảo hiểm vật chất (%)</span><span class="text-[10px] text-indigo-600 font-bold">Biểu phí</span></label>
                        <input type="number" id="live-bhvc-rate" step="0.01" min="0" autocomplete="off" placeholder="Theo biểu phí">
                        <div id="live-bhvc-rate-help" class="live-help">Tự đối chiếu theo giá xe sau giảm.</div>
                        <button type="button" onclick="applyRecommendedBhvcRate()" class="tactile-btn mt-2 w-full py-1.5 px-3 rounded-lg bg-indigo-50 text-indigo-700 border border-indigo-200 text-[11px] font-black hover:bg-indigo-100 flex items-center justify-center gap-1">
                            <span>⚡ Áp dụng tỷ lệ chuẩn</span>
                        </button>
                    </div>
                </div>

                <div class="live-fee-row">
                    <div class="live-field">
                        <label><span>Hãng Bảo hiểm phân phối</span></label>
                        <select id="live-bhvc-insurer" class="w-full border rounded-lg px-3 py-2 bg-white">
                            <option value="PJICO">PJICO</option>
                            <option value="DBV">DBV (BT - Tối thiểu 5tr)</option>
                            <option value="MIC">MIC</option>
                            <option value="BIC">BIC (Tối thiểu 5,5tr)</option>
                            <option value="BAOVIET">Bảo Việt (Theo Model)</option>
                        </select>
                        <div class="live-help">DBV tối thiểu 5 triệu · BIC tối thiểu 5,5 triệu · EC VAN BIC 1,30% · Bảo Việt theo Model.</div>
                    </div>
                    <div class="live-field">
                        <label><span>Loại hình sử dụng xe</span></label>
                        <select id="live-bhvc-vehicle-class" class="w-full border rounded-lg px-3 py-2 bg-white">
                            <option value="auto">Tự động theo mục đích sử dụng</option>
                            <option value="nonbusiness">Xe không kinh doanh</option>
                            <option value="business">Xe chở người kinh doanh</option>
                            <option value="taxi">Xe Taxi</option>
                        </select>
                        <div id="live-bhvc-table-help" class="live-help">Gia đình = không KD; Dịch vụ = chở người KD; Xanh SM = Taxi.</div>
                    </div>
                </div>

                <div class="live-fee-row">
                    <div class="live-field">
                        <label><span>Giá BHVC nhập tay trực tiếp (VNĐ)</span></label>
                        <input type="text" id="live-bhvc-manual-amount" autocomplete="off" placeholder="Để trống = tính theo tỷ lệ">
                        <div id="live-bhvc-manual-help" class="live-help">Chỉ ghi đè số tiền BHVC, không thay đổi tỷ lệ.</div>
                        <button type="button" onclick="resetBhvcManualAmount()" class="tactile-btn mt-2 w-full py-1.5 px-3 rounded-lg bg-rose-50 text-rose-700 border border-rose-200 text-[11px] font-black hover:bg-rose-100">
                            Reset về tính theo tỷ lệ
                        </button>
                    </div>
                    <div class="live-field">
                        <label><span>Thuế trước bạ tùy chỉnh (nếu có)</span></label>
                        <input type="text" id="live-tax-adjust" autocomplete="off" placeholder="Mặc định xe điện 0%">
                    </div>
                </div>
            </div>

        </div>

        <!-- Sticky Modal Bottom Action Bar -->
        <div class="sticky bottom-0 bg-white/95 backdrop-blur-md pt-3.5 pb-4 px-6 border-t border-slate-200 flex items-center justify-between gap-3 shadow-md rounded-b-[27px] z-20">
            <button type="button" onclick="resetLiveCustomize()" class="tactile-btn px-4 py-2.5 rounded-xl border border-slate-300 bg-white text-slate-700 text-xs font-bold hover:bg-slate-50 flex items-center gap-1.5">
                <span>↻ Khôi phục chuẩn ban đầu</span>
            </button>
            <button type="button" onclick="toggleLiveCustomize(false); showMagicToast('Đã áp dụng toàn bộ biểu phí mới thành công!', '✓')" class="tactile-btn px-6 py-2.5 rounded-xl bg-gradient-to-r from-purple-600 via-indigo-600 to-blue-600 text-white text-xs font-black shadow-lg shadow-purple-600/30 hover:brightness-110 flex items-center gap-1.5">
                <span>✓ Hoàn Tất & Áp Dụng</span>
            </button>
        </div>
    </div>

    <!-- ================= MAIN STUDIO WORKSPACE CONTAINER ================= -->
    <div class="max-w-[1560px] mx-auto flex flex-col xl:flex-row gap-7 p-4 xl:p-8 items-start justify-center pb-28 sm:pb-36 relative z-10">
        
        <!-- ================= LỆNH ĐIỀU KHIỂN BÊN TRÁI (STUDIO CONSOLE) ================= -->
        <div id="left-console" class="flex flex-col gap-5 w-full xl:w-[470px] shrink-0 xl:sticky top-20 z-10">
            
            <!-- CARD 1: CẤU HÌNH DÒNG XE & KHÁCH HÀNG (QUICK HERO SWITCHER) -->
            <div class="el-console-card tactile-card">
                <div class="p-4 bg-gradient-to-r from-slate-900 via-blue-950 to-slate-900 text-white flex items-center justify-between border-b border-blue-900/40">
                    <div class="flex items-center gap-2.5">
                        <span class="w-2.5 h-2.5 rounded-full bg-cyan-400 animate-pulse"></span>
                        <h3 class="font-display font-extrabold text-[15px] uppercase tracking-wide text-white">Dòng Xe Đang Tư Vấn</h3>
                    </div>
                    <span id="studio-hero-price" class="text-xs font-mono font-black text-cyan-300 bg-blue-900/60 px-2.5 py-1 rounded-lg border border-cyan-400/30">0 VNĐ</span>
                </div>
                <div class="p-5 space-y-3.5">
                    <div>
                        <div class="flex items-center justify-between mb-1.5">
                            <label class="text-xs font-bold text-gray-700">Chuyển Dòng Xe Nhanh</label>
                            <span id="studio-hero-model" class="text-[11px] font-semibold text-blue-600">Đang tải...</span>
                        </div>
                        <div class="relative bg-blue-50/70 rounded-xl border-2 border-blue-200 h-12 flex items-center px-3 hover:border-blue-400 transition-colors">
                            <svg class="w-5 h-5 text-blue-600 mr-2 shrink-0" fill="currentColor" viewBox="0 0 512 512"><path d="M135.2 117.4L109.1 192H402.9l-26.1-74.6C372.3 104.6 360.2 96 346.6 96H165.4c-13.6 0-25.7 8.6-30.2 21.4zM39.6 196.8L74.8 96.3C88.3 57.8 124.6 32 165.4 32H346.6c40.8 0 77.1 25.8 90.6 64.3l35.2 100.5c23.2 9.6 39.6 32.5 39.6 59.2V400v48c0 17.7-14.3 32-32 32H448c-17.7 0-32-14.3-32-32V400H96v48c0 17.7-14.3 32-32 32H32c-17.7 0-32-14.3-32-32V400V256c0-26.7 16.4-49.6 39.6-59.2zM128 288a32 32 0 1 0 -64 0 32 32 0 1 0 64 0zm288 32a32 32 0 1 0 0-64 32 32 0 1 0 0 64z"/></svg>
                            <select id="consoleCarSelect" onchange="handleConsoleCarChange(this.value)" class="font-bold text-gray-800 text-sm h-full w-full outline-none bg-transparent cursor-pointer"></select>
                        </div>
                    </div>

                    <!-- GIAO DIỆN CHỌN MÀU SẮC CHO XE TẠI STUDIO CONSOLE -->
                    <div class="pt-2.5 border-t border-blue-100">
                        <div class="flex items-center justify-between mb-2">
                            <label class="text-xs font-bold text-gray-700 flex items-center gap-1.5">
                                <span class="w-2.5 h-2.5 rounded-full bg-blue-600"></span>
                                <span>Màu Ngoại Thất Xe</span>
                            </label>
                            <span id="console-selected-color-name" class="text-[11px] font-bold text-blue-700 bg-blue-100 px-2 py-0.5 rounded-md">--</span>
                        </div>
                        <div id="console-color-swatches" class="flex flex-wrap gap-2 p-2.5 bg-slate-50 rounded-xl border border-slate-200/90 min-h-[48px] items-center"></div>
                    </div>

                    <div class="flex items-center justify-between pt-1 text-[11px] text-slate-500">
                        <span>Biển số, Màu, Hộ khẩu & Thanh toán chỉnh trực tiếp trên Báo giá</span>
                        <button type="button" onclick="document.getElementById('carSelect')?.focus()" class="tactile-btn text-blue-600 font-bold hover:underline">Chi tiết ↗</button>
                    </div>
                </div>
            </div>

            <!-- CARD 2: CÔNG CỤ TÍNH KM VINFAST -->
            <div class="el-console-card tactile-card">
                <div class="el-console-header text-white flex items-center justify-between">
                    <div>
                        <h3 class="font-display font-extrabold text-[15px] uppercase tracking-wide flex items-center gap-2">
                            <svg class="w-5 h-5 text-cyan-300" fill="currentColor" viewBox="0 0 512 512"><path d="M256 0c4.6 0 9.2 1 13.4 2.9L457.7 82.8c22 9.3 38.4 31 38.3 57.2c-.5 99.2-41.3 280.7-213.6 363.2c-16.7 8-36.1 8-52.8 0C57.3 420.7 16.5 239.2 16 140c-.1-26.2 16.3-47.9 38.3-57.2L242.7 2.9C246.8 1 251.4 0 256 0z"/></svg>
                            <span>Khuyến Mãi VinFast</span>
                        </h3>
                        <p class="text-[11px] text-blue-200 mt-0.5">Chính sách đồng bộ từ Quản Lý CTKM chuẩn 2026</p>
                    </div>
                    <button type="button" onclick="openPromoManager()" class="tactile-btn px-2.5 py-1 rounded-lg bg-white/20 hover:bg-white/30 text-white text-[10px] font-bold border border-white/20">
                        Cấu hình
                    </button>
                </div>
                
                <div class="p-5 space-y-4">
                    <!-- CTKM ĐẶC QUYỀN (CHỌN 1) -->
                    <div>
                        <label class="block text-xs font-bold text-gray-700 mb-1.5 flex items-center justify-between">
                            <span>CTKM Đặc Quyền (Chỉ chọn 1)</span>
                            <span class="text-[10px] font-bold text-blue-600 uppercase">Ưu đãi độc quyền</span>
                        </label>
                        <div id="vf-main-policy-container"></div>
                    </div>

                    <!-- MỨC GIẢM TỐI ĐA NHÀ MÁY THEO DÒNG XE -->
                    <div class="bg-gradient-to-r from-amber-50 to-orange-50 border border-amber-300 rounded-xl p-3 shadow-sm">
                        <div class="flex items-center justify-between gap-3">
                            <div>
                                <div class="text-xs font-black text-amber-900 uppercase tracking-wide">Mức giảm tối đa Nhà máy</div>
                                <div class="text-[10px] text-amber-700 mt-0.5">Khung trần tham chiếu · Phần vượt chuyển sang Thanh Toán</div>
                            </div>
                            <div id="vf-car-cut-limit-display" class="text-base font-mono font-black text-amber-700 whitespace-nowrap bg-white/80 px-2.5 py-1 rounded-lg border border-amber-300">0 VNĐ</div>
                        </div>
                    </div>

                    <!-- GIẢM THÊM RIÊNG CỦA ĐẠI LÝ -->
                    <div id="vf-dealer-extra-panel" class="bg-blue-50/80 border-2 border-blue-200 rounded-xl p-4 shadow-sm space-y-2.5">
                        <div class="flex items-center justify-between gap-3">
                            <div>
                                <div class="text-xs font-black text-blue-900 uppercase tracking-wide">Ưu Đãi Riêng Đại Lý</div>
                                <div class="text-[10px] text-blue-600 mt-0.5">Giảm thêm bằng tiền hoặc quà tặng riêng</div>
                            </div>
                            <div class="text-right shrink-0">
                                <div class="text-[10px] uppercase font-bold text-blue-500">Gợi ý giảm</div>
                                <div id="vf-dealer-suggest" class="text-sm font-mono font-black text-blue-700">0 VNĐ</div>
                            </div>
                        </div>

                        <div id="vf-dealer-gift-wrap" class="hidden bg-white/90 border border-blue-200 rounded-lg p-2.5">
                            <div class="text-[10px] uppercase font-bold text-blue-600 mb-0.5">Gợi ý quà tặng Đại lý:</div>
                            <div id="vf-dealer-gift-suggest" class="text-xs font-semibold text-blue-800 leading-relaxed whitespace-pre-line"></div>
                        </div>

                        <div>
                            <label class="block text-[11px] font-bold text-gray-700 mb-1">Nhập mức giảm thêm bằng tiền (VNĐ)</label>
                            <input type="text" inputmode="numeric" id="vf-dealer-extra" oninput="formatInputMoney(this); syncVF()" placeholder="Nhập mức giảm thêm bằng tiền..." class="w-full border-2 border-blue-300 rounded-lg p-2.5 text-base font-mono font-black text-blue-800 text-right outline-none bg-white focus:ring-2 focus:ring-blue-200 focus:border-blue-500 transition-all">
                        </div>

                        <div class="flex items-center justify-between gap-2 pt-1 text-[11px]">
                            <span class="text-gray-500 text-[10px]">Tự chia Hóa đơn / Thanh toán</span>
                            <button type="button" onclick="applyDealerSuggestion()" class="tactile-btn shrink-0 px-3 py-1.5 rounded-lg bg-blue-600 text-white font-bold text-xs shadow hover:bg-blue-700">
                                Dùng mức gợi ý
                            </button>
                        </div>
                    </div>

                    <!-- CTKM BỔ SUNG (CỘNG DỒN) -->
                    <div>
                        <label class="block text-xs font-bold text-gray-700 mb-2 flex items-center justify-between">
                            <span>CTKM Bổ Sung Áp Dụng Cho Xe</span>
                            <span class="text-[10px] font-bold text-emerald-600 uppercase">Cộng dồn</span>
                        </label>
                        <div id="vf-additive-promos" class="space-y-2"></div>
                    </div>

                    <!-- CẮT MÁU (LƯƠNG SALE) -->
                    <div class="bg-rose-50 border-2 border-rose-300 rounded-xl p-3.5 shadow-sm relative overflow-hidden">
                        <div class="absolute right-0 top-0 w-2 h-full bg-rose-500"></div>
                        <div class="flex justify-between items-center mb-1">
                            <label class="block text-xs font-black text-rose-700 uppercase tracking-wide">Giảm Giá Bằng Lương Sale</label>
                        </div>
                        <div class="flex justify-between items-center text-[11px] text-rose-500 font-medium mb-2">
                            <span>Chiết khấu nội bộ giảm thêm</span>
                            <span id="vf-catmau-limit" class="font-bold text-rose-700 font-mono underline">MASP: --</span>
                        </div>
                        <input type="text" id="vf-catmau" oninput="formatInputMoney(this); syncVF()" placeholder="Nhập số tiền giảm bằng lương..." class="w-full border border-rose-300 rounded-lg p-2.5 text-base font-mono font-black text-rose-600 text-right outline-none bg-white focus:ring-2 focus:ring-rose-200 transition-all">
                    </div>
                </div>
            </div>

            <!-- CARD 3: BẢO HIỂM & PHỤ KIỆN -->
            <div class="el-console-card tactile-card">
                <div class="el-console-header el-console-header-purple text-white flex items-center justify-between">
                    <div>
                        <h3 class="font-display font-extrabold text-[15px] uppercase tracking-wide flex items-center gap-2">
                            <svg class="w-5 h-5 text-purple-200" fill="currentColor" viewBox="0 0 512 512"><path d="M40 48C26.7 48 16 58.7 16 72v48c0 13.3 10.7 24 24 24H88c13.3 0 24-10.7 24-24V72c0-13.3-10.7-24-24-24H40zM192 64c-17.7 0-32 14.3-32 32s14.3 32 32 32H480c17.7 0 32-14.3 32-32s-14.3-32-32-32H192zM16 232v48c0 13.3 10.7 24 24 24H88c13.3 0 24-10.7 24-24V232c0-13.3-10.7-24-24-24H40c-13.3 0-24 10.7-24 24zM192 224c-17.7 0-32 14.3-32 32s14.3 32 32 32H480c17.7 0 32-14.3 32-32s-14.3-32-32-32H192zM40 368c-13.3 0-24 10.7-24 24v48c0 13.3 10.7 24 24 24H88c13.3 0 24-10.7 24-24V392c0-13.3-10.7-24-24-24H40zM192 384c-17.7 0-32 14.3-32 32s14.3 32 32 32H480c17.7 0 32-14.3 32-32s-14.3-32-32-32H192z"/></svg>
                            <span>Bảo Hiểm & Phụ Kiện</span>
                        </h3>
                        <p class="text-[11px] text-purple-200 mt-0.5">Biểu phí chuẩn BHVC & Phụ kiện chính hãng</p>
                    </div>
                    <button type="button" onclick="openAccManager()" class="tactile-btn px-2.5 py-1 rounded-lg bg-white/20 hover:bg-white/30 text-white text-[10px] font-bold border border-white/20">
                        Cấu hình
                    </button>
                </div>

                <div class="p-5 space-y-4">
                    <!-- BHVC Radio Mode -->
                    <div id="left-bhvc-panel" class="flex flex-col gap-2"></div>

                    <!-- Insurers Quick Selection -->
                    <div id="bhvc-insurer-quick-select" class="left-insurer-select rounded-xl border border-blue-200 bg-blue-50/80 px-3 py-3">
                        <div class="insurer-title text-[11px] font-black uppercase text-blue-900 mb-2 flex items-center justify-between">
                            <span>Bảo hiểm phân phối</span>
                            <span class="text-[10px] text-blue-600 font-bold">Chọn 1 hãng</span>
                        </div>
                        <div class="insurer-options grid grid-cols-3 sm:grid-cols-5 gap-1.5 text-xs font-bold text-gray-700">
                            <label class="inline-flex items-center gap-1.5 p-1.5 rounded-lg bg-white border border-blue-100 hover:border-blue-400 cursor-pointer">
                                <input type="checkbox" id="bhvc-check-PJICO" data-bhvc-insurer="PJICO" checked onchange="selectBhvcInsurerCheckbox('PJICO', this)" class="w-4 h-4 accent-blue-600">
                                <span>PJICO</span>
                            </label>
                            <label class="inline-flex items-center gap-1.5 p-1.5 rounded-lg bg-white border border-blue-100 hover:border-blue-400 cursor-pointer">
                                <input type="checkbox" id="bhvc-check-DBV" data-bhvc-insurer="DBV" onchange="selectBhvcInsurerCheckbox('DBV', this)" class="w-4 h-4 accent-blue-600">
                                <span>DBV (BT)</span>
                            </label>
                            <label class="inline-flex items-center gap-1.5 p-1.5 rounded-lg bg-white border border-blue-100 hover:border-blue-400 cursor-pointer">
                                <input type="checkbox" id="bhvc-check-MIC" data-bhvc-insurer="MIC" onchange="selectBhvcInsurerCheckbox('MIC', this)" class="w-4 h-4 accent-blue-600">
                                <span>MIC</span>
                            </label>
                            <label class="inline-flex items-center gap-1.5 p-1.5 rounded-lg bg-white border border-blue-100 hover:border-blue-400 cursor-pointer">
                                <input type="checkbox" id="bhvc-check-BIC" data-bhvc-insurer="BIC" onchange="selectBhvcInsurerCheckbox('BIC', this)" class="w-4 h-4 accent-blue-600">
                                <span>BIC</span>
                            </label>
                            <label class="inline-flex items-center gap-1.5 p-1.5 rounded-lg bg-white border border-blue-100 hover:border-blue-400 cursor-pointer col-span-2 sm:col-span-1">
                                <input type="checkbox" id="bhvc-check-BAOVIET" data-bhvc-insurer="BAOVIET" onchange="selectBhvcInsurerCheckbox('BAOVIET', this)" class="w-4 h-4 accent-blue-600">
                                <span>Bảo Việt</span>
                            </label>
                        </div>
                        <div id="bhvc-insurer-quick-help" class="insurer-help text-[10px] text-blue-700 mt-2 font-medium">Mặc định PJICO · chỉ áp dụng 1 bảo hiểm tại một thời điểm.</div>
                    </div>

                    <!-- 4 Quick Accessory Action Buttons -->
                    <div class="grid grid-cols-2 gap-2 pt-1">
                        <button type="button" onclick="openAccPicker()" class="tactile-btn py-2.5 px-3 bg-purple-50 text-purple-700 hover:bg-purple-100 font-bold rounded-xl border border-purple-200 text-xs sm:text-sm flex items-center justify-center gap-1 shadow-sm">
                            <span>💳</span><span>+ Phụ Kiện Bán</span>
                        </button>
                        <button type="button" onclick="openComboPicker()" class="tactile-btn py-2.5 px-3 bg-indigo-50 text-indigo-700 hover:bg-indigo-100 font-bold rounded-xl border border-indigo-200 text-xs sm:text-sm flex items-center justify-center gap-1 shadow-sm">
                            <span>🎁</span><span>Quà Tặng Combo</span>
                        </button>
                        <button type="button" onclick="clearPurchasedAccessories()" class="tactile-btn py-2.5 px-3 bg-rose-50 text-rose-700 hover:bg-rose-100 font-bold rounded-xl border border-rose-200 text-xs flex items-center justify-center gap-1 shadow-sm">
                            <span>✕</span><span>Xóa PK mua</span>
                        </button>
                        <button type="button" onclick="clearGiftAccessories()" class="tactile-btn py-2.5 px-3 bg-amber-50 text-amber-700 hover:bg-amber-100 font-bold rounded-xl border border-amber-200 text-xs flex items-center justify-center gap-1 shadow-sm">
                            <span>✕</span><span>Xóa PK tặng</span>
                        </button>
                    </div>

                    <!-- Phụ kiện tặng linh động -->
                    <div class="rounded-xl border-2 border-emerald-200 bg-emerald-50/70 p-3.5 space-y-2">
                        <div class="flex items-center justify-between gap-2">
                            <div>
                                <div class="text-xs font-black text-emerald-800 uppercase tracking-wide">Phụ Kiện Tặng Linh Động</div>
                                <div class="text-[10px] text-emerald-700">Mỗi dòng là 1 món tặng hiển thị lên báo giá</div>
                            </div>
                            <button type="button" onclick="clearFlexibleGifts()" class="tactile-btn text-[10px] font-bold text-red-600 bg-white border border-red-200 rounded-lg px-2 py-1 hover:bg-red-50">
                                Xóa hết
                            </button>
                        </div>
                        <textarea id="flex-gift-input" rows="3" oninput="syncFlexibleGifts()" placeholder="VD:&#10;Thảm sàn cao cấp&#10;Dán phim cách nhiệt&#10;Camera hành trình" class="w-full resize-y border border-emerald-300 rounded-lg p-2.5 text-xs font-semibold text-gray-800 outline-none bg-white focus:ring-2 focus:ring-emerald-200 focus:border-emerald-500"></textarea>
                        <div id="flex-gift-count" class="text-[10px] text-emerald-700 font-bold text-right">0 món tặng</div>
                    </div>

                    <!-- Summary of selected accessories -->
                    <div id="left-acc-summary" class="flex flex-col gap-2 pt-1"></div>
                </div>
            </div>
        </div>

        <!-- ================= KHU VỰC BÁO GIÁ TRỰC TIẾP (RIGHT LIVE QUOTE STUDIO) ================= -->
        <div class="flex-1 min-w-0 flex flex-col items-center w-full">
            
            <!-- STUDIO CANVAS TOP CONTROL BAR (Scale / Zoom & Quick Export) -->
            <div id="quote-zoom-bar" class="w-full max-w-[1024px] mb-3 flex flex-wrap items-center justify-between gap-2.5 px-3 py-2 bg-white/90 backdrop-blur-md rounded-2xl border border-slate-200/80 shadow-sm">
                <div class="flex items-center gap-1.5 text-xs">
                    <span class="text-slate-400 font-bold mr-1">🔍 Thu phóng:</span>
                    <button type="button" data-scale="0.75" onclick="setQuoteViewScale(0.75)" class="zoom-pill-btn tactile-btn px-2.5 py-1 rounded-lg border border-slate-200 bg-white text-slate-700 font-bold hover:bg-slate-50 text-[11px]">75%</button>
                    <button type="button" data-scale="0.85" onclick="setQuoteViewScale(0.85)" class="zoom-pill-btn tactile-btn px-2.5 py-1 rounded-lg border border-slate-200 bg-white text-slate-700 font-bold hover:bg-slate-50 text-[11px]">85%</button>
                    <button type="button" data-scale="1" onclick="setQuoteViewScale(1)" class="zoom-pill-btn tactile-btn px-2.5 py-1 rounded-lg border border-blue-600 bg-blue-600 text-white font-bold text-[11px]">100%</button>
                    <button type="button" data-scale="fit" onclick="setQuoteViewScale('fit')" class="zoom-pill-btn tactile-btn px-2.5 py-1 rounded-lg border border-slate-200 bg-white text-slate-700 font-bold hover:bg-slate-50 text-[11px]">⛶ Vừa Màn Hình</button>
                </div>
                
                <div class="flex items-center gap-2">
                    <span class="text-[11px] text-slate-500 font-medium hidden sm:inline">Khổ in chuẩn 1024px HD</span>
                    <button type="button" onclick="openPreview()" class="tactile-btn px-3 py-1 rounded-xl bg-blue-50 text-blue-700 border border-blue-200 font-bold text-xs hover:bg-blue-100 flex items-center gap-1">
                        <span>📸</span><span>Xem Bản In</span>
                    </button>
                    <button type="button" onclick="savePreviewPdf('full', this)" class="tactile-btn px-3 py-1 rounded-xl bg-rose-50 text-rose-700 border border-rose-200 font-bold text-xs hover:bg-rose-100 flex items-center gap-1">
                        <span>📄</span><span>PDF</span>
                    </button>
                </div>
            </div>

            <!-- QUOTE SHELL WRAPPER -->
            <div id="quote-live-shell" class="w-full max-w-[1024px] overflow-x-auto shrink-0 shadow-xl rounded-2xl bg-white border border-slate-200/80 transition-all duration-300">
                <div id="capture-area" class="relative bg-white w-[1024px] min-w-[1024px]">
                    <!-- Header -->
                    <header class="flex items-center justify-between p-7 border-b-[5px] border-brand-primary bg-white rounded-t-lg">
                        <div>
                            <h1 class="text-xl font-bold tracking-wide text-brand-dark">VINFAST THẾ TÀI</h1>
                            <div class="flex items-center gap-2 mt-1 flex-wrap">
                                <p class="text-xs text-gray-500 uppercase tracking-widest font-semibold">Đại lý ủy quyền chính hãng</p>
                                <span class="text-[12px] font-black text-brand-primary tracking-wide">• SĐT 0772993837</span>
                            </div>
                        </div>
                        <div class="text-right"><p class="text-sm text-gray-500 italic mt-1" id="current-date">Ngày lập: --/--/----</p></div>
                    </header>

                    <div class="p-7 space-y-7 bg-white">
                        <!-- Section 1: Vehicle Title, Quick Dropdowns & Pricing Breakdown Card -->
                        <div class="capture-grid-main">
                            <div class="capture-col quote-intro-card">
                                <h3 class="text-xs font-bold text-gray-400 uppercase tracking-wide mb-1">Kính gửi quý khách hàng</h3>
                                <h2 id="quote-car-name" class="text-[28px] leading-tight font-extrabold text-brand-primary mb-2">Đang tải...</h2>
                                
                                <div class="quote-primary-row flex gap-3 text-sm mt-4">
                                    <div class="relative bg-gray-100 rounded-md border-2 border-transparent h-10 flex items-center px-3 w-[220px]">
                                        <svg class="w-4 h-4 text-gray-500 mr-2 shrink-0" fill="currentColor" viewBox="0 0 512 512"><path d="M135.2 117.4L109.1 192H402.9l-26.1-74.6C372.3 104.6 360.2 96 346.6 96H165.4c-13.6 0-25.7 8.6-30.2 21.4zM39.6 196.8L74.8 96.3C88.3 57.8 124.6 32 165.4 32H346.6c40.8 0 77.1 25.8 90.6 64.3l35.2 100.5c23.2 9.6 39.6 32.5 39.6 59.2V400v48c0 17.7-14.3 32-32 32H448c-17.7 0-32-14.3-32-32V400H96v48c0 17.7-14.3 32-32 32H32c-17.7 0-32-14.3-32-32V400V256c0-26.7 16.4-49.6 39.6-59.2zM128 288a32 32 0 1 0 -64 0 32 32 0 1 0 64 0zm288 32a32 32 0 1 0 0-64 32 32 0 1 0 0 64z"/></svg>
                                        <select id="carSelect" onchange="handleCarSelectionChange()" class="font-semibold text-gray-700 h-full w-full outline-none bg-transparent"></select>
                                    </div>
                                    <div id="plate-wrapper" class="relative bg-gray-100 rounded-md border-2 border-transparent h-10 flex items-center px-3 w-[150px]">
                                        <svg id="plate-icon" class="w-4 h-4 text-gray-500 mr-2 shrink-0" fill="currentColor" viewBox="0 0 576 512"><path d="M0 96l576 0c0-35.3-28.7-64-64-64H64C28.7 32 0 60.7 0 96zm0 32V416c0 35.3 28.7 64 64 64H512c35.3 0 64-28.7 64-64V128L0 128zm64 64H256c17.7 0 32 14.3 32 32v96c0 17.7-14.3 32-32 32H64c-17.7 0-32-14.3-32-32V224c0-17.7 14.3-32 32-32zm384-32a32 32 0 1 1 0 64 32 32 0 1 1 0-64zM320 320c0-17.7 14.3-32 32-32H480c17.7 0 32 14.3 32 32s-14.3 32-32 32H352c-17.7 0-32-14.3-32-32z"/></svg>
                                        <select id="plateSelect" onchange="syncPlateSelection()" class="font-semibold text-gray-700 h-full w-full outline-none bg-transparent">
                                            <option value="trang" selected>Biển trắng</option><option value="vang">Biển vàng</option><option value="congty">Xe Công Ty</option>
                                        </select>
                                    </div>
                                </div>
                                <div class="quote-option-grid">
                                    <div id="color-wrapper" class="quote-option color-option-wrap">
                                        <div class="color-option-main">
                                            <label>Màu</label>
                                            <select id="colorSelect" onchange="syncCarColor(this.value)"></select>
                                        </div>
                                        <div id="color-surcharge-hint" class="hidden color-surcharge-hint"></div>
                                    </div>
                                    <div class="quote-option" id="payment-wrapper">
                                        <label>TT</label>
                                        <select id="paymentSelect" onchange="updateQuotationUI()"><option value="CASH" selected>CASH</option><option value="BANK">BANK</option></select>
                                    </div>
                                    <div class="quote-option" id="city-plate-wrapper">
                                        <label>Hộ khẩu</label>
                                        <select id="cityPlateSelect" onchange="syncRegistrationFromCityPlate(); updateQuotationUI()">
                                            <option value="tinh" selected>Tỉnh</option>
                                            <option value="thanhpho">TP (+14Tr)</option>
                                        </select>
                                    </div>
                                    <div class="quote-option" id="usage-wrapper">
                                        <label>Sử dụng</label>
                                        <select id="usageSelect" onchange="syncChargingUsage()">
                                            <option value="family" selected>Gia đình</option>
                                            <option value="service">Dịch vụ</option>
                                            <option value="xanhsm">Độc quyền Xanh SM</option>
                                        </select>
                                        <div id="usage-rule-note" class="hidden text-[8px] font-bold text-rose-600 mt-1 leading-tight"></div>
                                    </div>
                                </div>
                                <div class="quote-fee-option-grid">
                                    <div class="quote-option">
                                        <label onclick="toggleLiveCustomize(true)" class="cursor-pointer hover:text-purple-600 transition-colors flex items-center gap-0.5" title="Nhấn để tùy chỉnh chi tiết"><span>Phí ĐK</span><span class="text-[9px] text-purple-500">✎</span></label>
                                        <select id="quoteRegistrationPreset" onchange="syncQuoteFeePreset('registration')">
                                            <option value="ward">Phường/Xã · 140.000</option>
                                            <option value="metro">TP.HCM/HN · 14.000.000</option>
                                            <option value="custom">Tùy chỉnh...</option>
                                        </select>
                                    </div>
                                    <div class="quote-option">
                                        <label onclick="toggleLiveCustomize(true)" class="cursor-pointer hover:text-purple-600 transition-colors flex items-center gap-0.5" title="Nhấn để tùy chỉnh chi tiết"><span>Đăng kiểm</span><span class="text-[9px] text-purple-500">✎</span></label>
                                        <select id="quoteInspectionPreset" onchange="syncQuoteFeePreset('inspection')">
                                            <option value="57">Xe 5/7 chỗ · 90.000</option>
                                            <option value="custom">Tùy chỉnh...</option>
                                        </select>
                                    </div>
                                    <div class="quote-option">
                                        <label onclick="toggleLiveCustomize(true)" class="cursor-pointer hover:text-purple-600 transition-colors flex items-center gap-0.5" title="Nhấn để tùy chỉnh chi tiết"><span>BHDS</span><span class="text-[9px] text-purple-500">✎</span></label>
                                        <select id="quoteCivilPreset" onchange="syncQuoteFeePreset('civil')">
                                            <option value="family4">Gia đình 4 chỗ · 520.700</option>
                                            <option value="family5">Gia đình 5 chỗ · 530.700</option>
                                            <option value="family7">Gia đình 7 chỗ · 1.013.400</option>
                                            <option value="taxi5">Taxi 5 chỗ · 1.443.720</option>
                                            <option value="taxi7">Taxi 7 chỗ · 2.049.600</option>
                                            <option value="business5">KD UDCN 5 chỗ · 861.600</option>
                                            <option value="business7">KD UDCN 7 chỗ · 1.218.000</option>
                                            <option value="custom">Tùy chỉnh...</option>
                                        </select>
                                    </div>
                                    <div class="quote-option">
                                        <label onclick="toggleLiveCustomize(true)" class="cursor-pointer hover:text-purple-600 transition-colors flex items-center gap-0.5" title="Nhấn để tùy chỉnh chi tiết"><span>Đường bộ</span><span class="text-[9px] text-purple-500">✎</span></label>
                                        <select id="quoteRoadPreset" onchange="syncQuoteFeePreset('road')">
                                            <option value="white1">Biển trắng 1 năm · 1.560.000</option>
                                            <option value="white3">Biển trắng 3 năm · 4.325.000</option>
                                            <option value="yellow1">Biển vàng/Van/Bán tải · 2.160.000</option>
                                            <option value="custom">Tùy chỉnh...</option>
                                        </select>
                                    </div>
                                </div>
                            </div>

                            <div class="capture-col quote-price-card text-[14px]">
                                <div class="quote-price-row"><span class="font-medium text-gray-600">Giá niêm yết</span><div class="dot-leader"></div><span id="quote-price-listed" class="font-bold text-gray-900">0 VNĐ</span></div>
                                <div class="quote-price-row text-brand-primary"><span class="font-semibold">Tổng ưu đãi</span><div class="dot-leader"></div><span id="quote-discount" class="font-black">- 0 VNĐ</span></div>
                                <div id="quote-invoice-discount-row" class="hidden quote-price-row text-emerald-700"><span class="font-semibold">Giảm trên HĐ Đại lý</span><div class="dot-leader"></div><span id="quote-invoice-discount" class="font-black">- 0 VNĐ</span></div>
                                <div class="quote-price-row"><span class="font-medium text-gray-700">Giá Đại lý xuất HĐ</span><div class="dot-leader"></div><span id="quote-invoice-price" class="font-black text-emerald-700">0 VNĐ</span></div>
                                <div class="quote-price-row quote-price-final-row"><span class="font-black text-gray-900 uppercase text-[12px]">Giá xe theo hóa đơn</span><div class="dot-leader"></div><span id="quote-price-final" class="font-black text-brand-primary">0 VNĐ</span></div>
                            </div>
                        </div>

                        <!-- Section 2: V-Green Charging Promo Card -->
                        <div id="charging-promo-panel" class="rounded-xl border border-cyan-200 bg-cyan-50/70 overflow-hidden shadow-sm">
                            <div class="px-4 py-3 bg-gradient-to-r from-cyan-100/90 to-blue-100/90 border-b border-cyan-200">
                                <div class="flex items-center justify-between gap-3">
                                    <div class="text-[12px] font-black text-cyan-900 uppercase flex items-center gap-1.5">
                                        <span>⚡</span><span>Ưu Đãi Sạc V-Green</span>
                                    </div>
                                    <div class="text-[10px] font-bold text-cyan-800 bg-white/70 px-2 py-0.5 rounded-full border border-cyan-300">CS 19/09/2026</div>
                                </div>
                                <div id="charging-promo-summary" class="text-xs text-cyan-950 font-semibold leading-relaxed mt-1.5">—</div>
                            </div>
                            <div class="border-t border-cyan-200 bg-white/80 px-4 py-3">
                                <div class="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[10px]">
                                    <div class="rounded-lg border border-cyan-100 bg-white px-3 py-2">
                                        <div class="font-black text-gray-600 uppercase">Thứ Hai - Thứ Năm</div>
                                        <div class="font-bold text-emerald-700 mt-0.5">Biển vàng: áp dụng cả ngày</div>
                                    </div>
                                    <div class="rounded-lg border border-cyan-100 bg-white px-3 py-2">
                                        <div class="font-black text-gray-600 uppercase">Thứ Sáu - Chủ Nhật</div>
                                        <div class="font-bold text-amber-700 mt-0.5">23:00-06:00 và 14:00-16:00</div>
                                    </div>
                                </div>
                                <div id="charging-current-window" class="mt-2 rounded-lg bg-cyan-100/70 px-3 py-2 text-[10px] font-black text-cyan-900"></div>
                                <div id="charging-cycle-info" class="mt-1 text-[9px] text-cyan-800 font-semibold"></div>
                                <div class="mt-2 text-[9px] text-gray-500 leading-relaxed">
                                    * Khung giờ trên áp dụng cho khách hàng xe Biển vàng mua từ 20/04/2026.
                                    Số lần sạc được tính từ ngày 26 tháng trước đến hết ngày 25 tháng tiếp theo.
                                </div>
                            </div>
                        </div>

                        <!-- Section 3: Warranty Card -->
                        <div id="warranty-panel" class="rounded-xl border border-emerald-200 bg-emerald-50/60 overflow-hidden shadow-sm">
                            <div class="px-4 py-3 bg-gradient-to-r from-emerald-100/90 to-teal-100/90 border-b border-emerald-200 flex items-center justify-between gap-3">
                                <div>
                                    <div class="text-[13px] font-black text-emerald-900 uppercase flex items-center gap-1.5">
                                        <span>🛡️</span><span>Thông Tin Bảo Hành Chính Hãng</span>
                                    </div>
                                    <div id="warranty-subtitle" class="text-[10px] text-emerald-700 font-bold mt-0.5"></div>
                                </div>
                                <div class="flex flex-wrap gap-2 justify-end">
                                    <button type="button" onclick="openMaintenanceSchedule()" class="tactile-btn text-[10px] font-black text-blue-700 bg-white border border-blue-300 rounded-lg px-3 py-1.5 shadow-sm hover:bg-blue-50">Mốc bảo dưỡng</button>
                                    <button type="button" onclick="toggleWarrantyDetails()" class="tactile-btn text-[10px] font-black text-emerald-800 bg-white border border-emerald-300 rounded-lg px-3 py-1.5 shadow-sm hover:bg-emerald-50">Xem chi tiết</button>
                                </div>
                            </div>
                            <div class="p-4 grid grid-cols-1 sm:grid-cols-2 gap-3">
                                <div class="rounded-xl bg-white border border-emerald-200 p-3 shadow-sm">
                                    <div class="text-[10px] uppercase font-black text-gray-500">Bảo hành xe mới</div>
                                    <div id="warranty-vehicle-main" class="text-base font-black text-emerald-800 mt-1">—</div>
                                    <div id="warranty-vehicle-note" class="text-[10px] text-gray-500 mt-1"></div>
                                </div>
                                <div class="rounded-xl bg-white border border-emerald-200 p-3 shadow-sm">
                                    <div class="text-[10px] uppercase font-black text-gray-500">Pin cao áp</div>
                                    <div id="warranty-battery-main" class="text-base font-black text-emerald-800 mt-1">—</div>
                                    <div id="warranty-battery-note" class="text-[10px] text-gray-500 mt-1"></div>
                                </div>
                            </div>
                            <div id="warranty-details" class="hidden px-4 pb-4">
                                <div class="rounded-xl border border-emerald-200 bg-white overflow-hidden shadow-sm">
                                    <div class="grid grid-cols-[1.3fr_1fr] text-[11px] font-bold">
                                        <div class="px-3 py-2 border-b bg-gray-50">Hạng mục</div><div class="px-3 py-2 border-b bg-gray-50">Thời hạn</div>
                                        <div class="px-3 py-2 border-b">Ắc quy 12V</div><div id="warranty-12v" class="px-3 py-2 border-b">—</div>
                                        <div class="px-3 py-2 border-b">Ghế xe</div><div id="warranty-seat" class="px-3 py-2 border-b">—</div>
                                        <div class="px-3 py-2 border-b">Sơn ngoại thất</div><div id="warranty-paint" class="px-3 py-2 border-b">—</div>
                                        <div class="px-3 py-2 border-b">Hệ thống treo*</div><div id="warranty-suspension" class="px-3 py-2 border-b">—</div>
                                        <div class="px-3 py-2 border-b">Lốp xe</div><div class="px-3 py-2 border-b">Theo chính sách NSX lốp</div>
                                        <div class="px-3 py-2">Phụ tùng hao mòn**</div><div class="px-3 py-2">6 tháng / 10.000 km</div>
                                    </div>
                                </div>
                                <div class="text-[9px] text-gray-500 mt-2 leading-relaxed">
                                    * Bộ giảm xóc, thanh ổn định, cụm liên kết trên, cánh tay điều khiển dưới, khớp bi, giá đỡ phía trên giảm xóc.<br>
                                    ** Má phanh, đĩa phanh, cao su gạt mưa, pin điều khiển, cầu chì 12V, bóng đèn sợi đốt và các chi tiết hao mòn tương đương.
                                </div>
                            </div>
                        </div>

                        <!-- Section 4: Vehicle Showroom Stage, Swatches & Specifications -->
                        <div class="quote-spec-card border border-gray-200 rounded-xl bg-white shadow-sm overflow-hidden">
                            <div class="grid grid-cols-1 lg:grid-cols-[1.8fr_1fr] min-h-[300px]">
                                <!-- Vehicle Stage with Pedestal Light Floor -->
                                <div class="car-stage-bg flex items-center justify-center p-5 min-w-0 overflow-hidden relative group">
                                    <div class="cyber-pedestal-rings"></div>
                                    <img id="quote-car-img" onerror="handleQuoteCarImageError(this)" class="max-w-full max-h-[330px] object-contain drop-shadow-2xl relative z-10 transition-transform duration-300 ease-out group-hover:scale-105" />
                                </div>
                                <div class="p-5 border-t lg:border-t-0 lg:border-l border-gray-100 bg-white">
                                    <div class="flex items-center justify-between gap-3">
                                        <h3 class="text-sm font-black text-brand-dark uppercase">Ngoại thất</h3>
                                        <span id="quote-selected-color" class="text-xs font-bold text-gray-600">—</span>
                                    </div>
                                    <div class="mt-4">
                                        <div class="text-[10px] font-bold text-gray-500 mb-2">Màu cơ bản - Theo xe</div>
                                        <div id="quote-basic-color-swatches" class="flex flex-wrap gap-2"></div>
                                    </div>
                                    <div id="quote-premium-color-wrap" class="mt-4">
                                        <div id="quote-premium-color-label" class="text-[10px] font-bold text-gray-500 mb-2">Màu nâng cao</div>
                                        <div id="quote-premium-color-swatches" class="flex flex-wrap gap-2"></div>
                                    </div>
                                    <div class="mt-5 pt-4 border-t">
                                        <div class="text-[10px] font-black uppercase text-gray-500 mb-2">Trang bị nổi bật</div>
                                        <ul id="quote-car-specs" class="space-y-2 text-[11px] text-gray-700"></ul>
                                    </div>
                                </div>
                            </div>

                            <!-- 3 Performance Gauges -->
                            <div class="grid grid-cols-3 border-t bg-slate-50/70">
                                <div class="p-4 text-center border-r border-gray-200/80">
                                    <div class="text-[10px] font-bold text-gray-500 uppercase mb-1">⚡ Công suất tối đa</div>
                                    <div id="quote-max-power" class="text-xl font-mono font-black text-gray-900">—</div>
                                </div>
                                <div class="p-4 text-center border-r border-gray-200/80">
                                    <div class="text-[10px] font-bold text-gray-500 uppercase mb-1">🔋 Dung lượng pin</div>
                                    <div id="quote-battery-capacity" class="text-xl font-mono font-black text-gray-900">—</div>
                                </div>
                                <div class="p-4 text-center">
                                    <div class="text-[10px] font-bold text-gray-500 uppercase mb-1">🛣️ Quãng đường di chuyển</div>
                                    <div id="quote-driving-range" class="text-xl font-mono font-black text-gray-900">—</div>
                                </div>
                            </div>
                        </div>

                        <!-- Section 5: Cost Breakdown Comparison Grid -->
                        <div class="capture-grid-cost">
                            <div class="capture-col flex flex-col min-w-0 export-hide-running-cost">
                                <h3 class="text-sm font-bold text-white bg-slate-900 py-2.5 px-4 rounded-t-lg uppercase shadow-sm">Chi phí lăn bánh</h3>
                                <div class="border border-slate-900 border-t-0 rounded-b-lg p-5 space-y-3.5 text-sm bg-white shadow-sm flex-1">
                                    <div class="flex justify-between items-end"><span id="quote-tax-label" class="text-gray-600">Lệ phí trước bạ (0%)</span><div class="dot-leader"></div><span id="quote-tax" class="font-bold">0 VNĐ</span></div>
                                    <div class="flex justify-between items-end"><span class="text-gray-600">Lệ phí đăng ký (Biển số)</span><div class="dot-leader"></div><span id="quote-phi-dang-ky" class="font-bold">140.000 VNĐ</span></div>
                                    <div class="flex justify-between items-end"><span class="text-gray-600">Lệ phí đăng kiểm</span><div class="dot-leader"></div><span id="quote-phi-dang-kiem" class="font-bold">90.000 VNĐ</span></div>
                                    <div class="flex justify-between items-end"><span class="text-gray-600">Lệ phí đường bộ</span><div class="dot-leader"></div><span id="quote-phi-duong-bo" class="font-bold">0 VNĐ</span></div>
                                    <div class="flex justify-between items-end"><span class="text-gray-600">Bảo hiểm dân sự</span><div class="dot-leader"></div><span id="quote-phi-tnds" class="font-bold">0 VNĐ</span></div>
                                    <div class="flex justify-between items-end"><span class="text-gray-600">Dịch vụ ĐK xe</span><div class="dot-leader"></div><span id="quote-phi-dich-vu" class="font-bold">0 VNĐ</span></div>
                                    <div id="quote-bu-thue-row" class="flex justify-between items-end" style="display:none;"><span class="text-gray-600">Bù thuế</span><div class="dot-leader"></div><span id="quote-bu-thue" class="font-bold">0 VNĐ</span></div>
                                    <div id="quote-bh-vc-row" class="flex justify-between items-end" style="display:none;"><span class="text-blue-700 font-bold">Bảo hiểm vật chất</span><div class="dot-leader border-blue-200"></div><span id="quote-bh-vc" class="font-bold text-blue-700">0 VNĐ</span></div>
                                    <div id="quote-acc-cost-row" class="flex justify-between items-end" style="display:none;"><span class="text-purple-700 font-bold">Option Phụ kiện</span><div class="dot-leader border-purple-200"></div><span id="quote-acc-cost" class="font-bold text-purple-700">0 VNĐ</span></div>
                                    <div id="quote-payment-discount-row" class="flex justify-between items-end text-blue-700" style="display:none;"><span class="font-bold">Giảm tại Thanh Toán</span><div class="dot-leader border-blue-200"></div><span id="quote-payment-discount" class="font-bold">- 0 VNĐ</span></div>
                                    <div class="flex justify-between items-end pt-3 border-t mt-3"><span class="font-bold text-gray-800 uppercase text-xs">Tổng chi phí ĐK sau giảm</span><div class="dot-leader"></div><span id="quote-reg-total" class="font-bold text-brand-primary text-base">0 VNĐ</span></div>
                                </div>
                            </div>

                            <div class="capture-col flex flex-col min-w-0">
                                <h3 class="text-sm font-bold text-white bg-emerald-600 py-2.5 px-4 rounded-t-lg uppercase shadow-sm">Chi tiết Khuyến mãi & Tri ân</h3>
                                <div class="border border-emerald-600 border-t-0 rounded-b-lg p-4 bg-emerald-50/50 flex-1 shadow-sm">
                                    <ul id="quote-promo-list" class="grid grid-cols-2 gap-2.5 items-start"></ul>
                                </div>
                            </div>
                        </div>

                        <!-- Section 6: Purchased Accessories List -->
                        <div id="quote-accessories-container" class="mt-6 export-hide-accessory-purchase" style="display: none;">
                            <h3 class="text-sm font-bold text-white bg-purple-600 py-2.5 px-4 rounded-t-lg uppercase shadow-sm">Danh Sách Phụ Kiện Mua Thêm</h3>
                            <div class="border border-purple-600 border-t-0 rounded-b-lg p-5 bg-purple-50/50 shadow-sm">
                                <ul id="quote-bought-acc-list" class="space-y-1.5 columns-2 gap-8"></ul>
                            </div>
                        </div>

                        <!-- Section 7: Bank Loan Section -->
                        <div id="bank-info-container" class="mt-6" style="display: none;">
                            <div class="flex gap-2 mb-3 export-hide-loan-schedule">
                                <button type="button" id="bank-tab-summary-btn" onclick="switchBankTab('summary')" class="tactile-btn px-4 py-2 rounded-xl border border-blue-600 bg-blue-600 text-white text-xs font-black shadow-sm">Thông tin vay</button>
                                <button type="button" id="bank-tab-schedule-btn" onclick="switchBankTab('schedule')" class="tactile-btn px-4 py-2 rounded-xl border border-blue-200 bg-white text-blue-700 text-xs font-black shadow-sm hover:bg-blue-50">Bảng trả góp</button>
                            </div>

                            <div id="bank-tab-summary-panel" class="capture-grid-cost">
                                <div class="capture-col flex flex-col min-w-0">
                                    <h3 class="text-sm font-bold text-white bg-blue-700 py-2.5 px-4 rounded-t-lg uppercase shadow-sm">Chính Sách Vay Ngân Hàng</h3>
                                    <div class="border border-blue-700 border-t-0 rounded-b-lg p-5 space-y-3.5 text-sm bg-white shadow-sm flex-1">
                                        <div class="flex justify-between items-end hover:bg-blue-50 px-2 -mx-2 rounded"><span class="text-gray-600">Tỷ lệ vay (%)</span><div class="dot-leader"></div><input type="number" id="bank-percent" class="w-16 text-right font-bold text-blue-700 outline-none border-b border-dashed border-gray-400" oninput="syncBank('percent')"></div>
                                        <div class="flex justify-between items-end hover:bg-blue-50 px-2 -mx-2 rounded"><span class="text-gray-600">Thời gian vay (Năm)</span><div class="dot-leader"></div><input type="number" id="bank-years" class="w-16 text-right font-bold text-blue-700 outline-none border-b border-dashed border-gray-400" oninput="syncBank('other')"></div>
                                        <div class="flex justify-between items-end hover:bg-blue-50 px-2 -mx-2 rounded"><span class="text-gray-600">Ưu đãi cố định</span><div class="dot-leader"></div><select id="bank-promo-months" class="font-bold text-blue-700 outline-none border-b border-dashed border-gray-400" onchange="syncBank('other')"><option value="6">6 Tháng</option><option value="12">12 Tháng</option><option value="24">24 Tháng</option></select></div>
                                        <div class="flex justify-between items-end hover:bg-blue-50 px-2 -mx-2 rounded"><span class="text-gray-600">Lãi suất ưu đãi (%/năm)</span><div class="dot-leader"></div><input type="number" id="bank-promo-rate" step="0.1" class="w-16 text-right font-bold text-blue-700 outline-none border-b border-dashed border-gray-400" oninput="syncBank('other')"></div>
                                        <div class="flex justify-between items-end hover:bg-blue-50 px-2 -mx-2 rounded">
                                            <span class="text-gray-600">Biên độ thả nổi (%/năm)</span>
                                            <div class="dot-leader"></div>
                                            <input type="number" id="bank-float-rate" step="0.1" class="w-16 text-right font-bold text-blue-700 outline-none border-b border-dashed border-gray-400" oninput="syncBank('other')">
                                        </div>
                                        <div class="pt-2 border-t text-[11px] text-gray-500">
                                            <div class="flex justify-between items-center mb-1">
                                                <span>Lãi suất tham chiếu Nhà nước (%/năm)</span>
                                                <input type="number" id="bank-state-rate" step="0.01" min="0" value="0" onchange="syncBank('stateRate')" class="w-16 text-right font-bold text-blue-700 outline-none border-b border-dashed border-gray-400">
                                            </div>
                                            <span class="text-[10px] text-gray-400 italic">Lãi thả nổi = Lãi tham chiếu Nhà nước + Biên độ.</span>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="capture-col flex flex-col min-w-0">
                                    <h3 class="text-sm font-bold text-white bg-blue-500 py-2.5 px-4 rounded-t-lg uppercase shadow-sm">Số Tiền Thanh Toán Nhận Xe</h3>
                                    <div class="border border-blue-500 border-t-0 rounded-b-lg p-5 bg-blue-50 flex-1 shadow-sm flex flex-col justify-center space-y-4">
                                        <div class="flex justify-between items-center bg-white p-3 rounded shadow-sm border border-blue-200"><span class="text-gray-600 text-sm font-semibold">Số tiền vay (NH giải ngân)</span><input type="text" id="bank-loan-amount" class="w-32 text-right font-bold text-blue-700 outline-none border-b border-dashed border-gray-400" oninput="formatInputMoney(this); syncBank('loan');"></div>
                                        <div class="flex justify-between items-center bg-white p-3 rounded shadow-sm border border-blue-200"><span class="text-gray-600 text-sm font-semibold">Số tiền đối ứng (Vốn tự có)</span><input type="text" id="bank-down-payment" class="w-32 text-right font-bold text-gray-800 outline-none border-b border-dashed border-gray-400" oninput="formatInputMoney(this); syncBank('down');"></div>
                                        <div class="flex justify-between items-end pt-3 mt-1 border-t border-blue-200"><div><span class="font-bold text-gray-800 uppercase text-sm block">Tổng thanh toán nhận xe</span><span class="text-[11px] text-gray-500 italic block">(Vốn đối ứng + Chi phí ĐK sau giảm)</span></div><span id="bank-total-pay" class="font-bold text-xl text-brand-primary">0 VNĐ</span></div>
                                        <div class="flex justify-between items-end pt-3 mt-1 border-t border-blue-200"><div><span class="font-bold text-blue-800 uppercase text-sm block">Trung bình trả góp 1 năm đầu</span></div><span id="bank-avg-monthly" class="font-bold text-lg text-blue-700 bg-blue-100 px-3 py-1 rounded shadow-sm">0 VNĐ / tháng</span></div>
                                    </div>
                                </div>
                            </div>

                            <div id="bank-tab-schedule-panel" class="hidden export-hide-loan-schedule">
                                <div class="rounded-xl border border-blue-200 bg-white overflow-hidden shadow-sm">
                                    <div class="px-4 py-3 bg-blue-50 border-b border-blue-200">
                                        <div class="font-black text-blue-900 uppercase text-sm">Bảng trả góp dự kiến theo dư nợ giảm dần</div>
                                        <div id="loan-schedule-note" class="text-[10px] text-blue-700 mt-1"></div>
                                    </div>

                                    <div class="grid grid-cols-2 md:grid-cols-5 gap-2 p-3 bg-slate-50 border-b">
                                        <div class="rounded-lg bg-white border p-2">
                                            <div class="text-[9px] uppercase font-black text-gray-500">Tổng lãi dự kiến</div>
                                            <div id="loan-stat-total-interest" class="text-sm font-black text-blue-700 mt-1">0 VNĐ</div>
                                        </div>
                                        <div class="rounded-lg bg-white border p-2">
                                            <div class="text-[9px] uppercase font-black text-gray-500">Lãi TB / tháng</div>
                                            <div id="loan-stat-avg-month" class="text-sm font-black text-blue-700 mt-1">0 VNĐ</div>
                                        </div>
                                        <div class="rounded-lg bg-white border p-2">
                                            <div class="text-[9px] uppercase font-black text-gray-500">Lãi TB / ngày</div>
                                            <div id="loan-stat-avg-day" class="text-sm font-black text-blue-700 mt-1">0 VNĐ</div>
                                        </div>
                                        <div class="rounded-lg bg-white border p-2">
                                            <div class="text-[9px] uppercase font-black text-gray-500">Đóng cao nhất</div>
                                            <div id="loan-stat-max-payment" class="text-sm font-black text-rose-700 mt-1">0 VNĐ</div>
                                        </div>
                                        <div class="rounded-lg bg-white border p-2">
                                            <div class="text-[9px] uppercase font-black text-gray-500">Đóng thấp nhất</div>
                                            <div id="loan-stat-min-payment" class="text-sm font-black text-emerald-700 mt-1">0 VNĐ</div>
                                        </div>
                                    </div>

                                    <div class="overflow-x-auto max-h-[520px] custom-scrollbar">
                                        <table class="w-full min-w-[720px] text-[11px]">
                                            <thead class="sticky top-0 bg-blue-900 text-white z-10">
                                                <tr>
                                                    <th class="px-3 py-2 text-center">Kỳ</th>
                                                    <th class="px-3 py-2 text-right">Dư nợ đầu kỳ</th>
                                                    <th class="px-3 py-2 text-right">Gốc</th>
                                                    <th class="px-3 py-2 text-right">Lãi</th>
                                                    <th class="px-3 py-2 text-right">Tổng Gốc + Lãi</th>
                                                    <th class="px-3 py-2 text-right">Lãi suất</th>
                                                </tr>
                                            </thead>
                                            <tbody id="loan-schedule-body"></tbody>
                                        </table>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Section 8: Total On Road Grand Footer -->
                    <div id="quote-total-footer" class="quote-total-footer bg-gradient-to-r from-blue-700 via-blue-600 to-blue-800 text-white px-7 py-8 flex justify-between items-center gap-6 rounded-b-lg border-b-8 border-brand-primary shadow-[0_-8px_28px_rgba(20,100,244,.18)]">
                        <div class="min-w-0">
                            <h2 class="text-[28px] font-black uppercase tracking-wider leading-tight">Tổng Giá Lăn Bánh</h2>
                            <p class="text-[14px] font-semibold text-blue-100 mt-1">Đã bao gồm VAT và các chi phí hợp lệ</p>
                        </div>
                        <div id="quote-total" class="text-[50px] font-black bg-white text-brand-primary px-9 py-4 rounded-2xl mr-1 shadow-2xl leading-none whitespace-nowrap border-2 border-blue-100 font-mono">0 VNĐ</div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- ================= FIXED BOTTOM BAR CÔNG CỤ (DÀNH CHO MOBILE) ================= -->
    <div id="action-buttons" class="fixed bottom-0 left-0 w-full z-40 flex xl:hidden overflow-x-auto bg-white/95 backdrop-blur-md border-t border-slate-200 p-2.5 gap-2 shadow-[0_-5px_20px_rgba(0,0,0,0.1)] hide-scroll items-center">
        <button onclick="openPreview()" class="tactile-btn bg-brand-primary text-white font-bold py-2.5 px-4 rounded-xl shadow-md shrink-0 text-xs whitespace-nowrap">📸 Lưu Hình</button>
        <button onclick="savePreviewPdf('full', this)" class="tactile-btn bg-rose-600 text-white font-bold py-2.5 px-4 rounded-xl shadow-md shrink-0 text-xs whitespace-nowrap">📄 Xuất PDF</button>
        <button onclick="openQuoteInfo()" class="tactile-btn bg-emerald-600 text-white font-bold py-2.5 px-4 rounded-xl shadow-md shrink-0 text-xs whitespace-nowrap">📋 Copy Text</button>
        <button onclick="toggleLiveCustomize(true)" class="tactile-btn bg-purple-600 text-white font-bold py-2.5 px-4 rounded-xl shadow-md shrink-0 text-xs whitespace-nowrap">⚙ Phí & Bank</button>
        <button onclick="openCarManager()" class="tactile-btn bg-blue-600 text-white font-bold py-2.5 px-4 rounded-xl shadow-md shrink-0 text-xs whitespace-nowrap">🚗 Dữ Liệu Xe</button>
        <button onclick="openPromoManager()" class="tactile-btn bg-fuchsia-600 text-white font-bold py-2.5 px-4 rounded-xl shadow-md shrink-0 text-xs whitespace-nowrap">🎯 CTKM</button>
        <button onclick="openAccManager()" class="tactile-btn bg-purple-600 text-white font-bold py-2.5 px-4 rounded-xl shadow-md shrink-0 text-xs whitespace-nowrap">📦 Phụ Kiện</button>
        <button onclick="openComboPicker()" class="tactile-btn bg-indigo-600 text-white font-bold py-2.5 px-4 rounded-xl shadow-md shrink-0 text-xs whitespace-nowrap">🎁 Combo</button>
        <button onclick="exportAllDataToFile()" class="tactile-btn bg-slate-700 text-white font-bold py-2.5 px-4 rounded-xl shadow-md shrink-0 text-xs whitespace-nowrap">⬇ Xuất Data</button>
        <label class="tactile-btn bg-amber-600 text-white font-bold py-2.5 px-4 rounded-xl shadow-md shrink-0 text-xs cursor-pointer mb-0 whitespace-nowrap">⬆ Nhập Data<input type="file" class="hidden" accept=".json" onchange="importAllDataFromFile(event)"></label>
    </div>

    <!-- ================== CÁC MODAL QUẢN LÝ DỮ LIỆU ================== -->

    <!-- 1. MODAL QUẢN LÝ XE -->
    <div id="carManagerModal" class="fixed inset-0 modal-backdrop-blur z-50 hidden justify-center items-center p-3 sm:p-5">
        <div class="bg-white w-full h-full sm:h-auto modal-content-box max-w-6xl max-h-full sm:max-h-[95vh] flex flex-col overflow-hidden">
            <div class="p-4 border-b flex justify-between items-center bg-slate-50 shrink-0">
                <div class="flex items-center gap-2">
                    <span class="text-xl">🚗</span>
                    <h2 class="text-lg sm:text-xl font-bold text-gray-800">Quản Lý Dữ Liệu Xe VinFast</h2>
                </div>
                <button onclick="closeCarManager()" class="tactile-btn w-9 h-9 rounded-full bg-slate-200 text-gray-700 hover:text-red-600 text-2xl flex items-center justify-center leading-none">&times;</button>
            </div>
            <div class="flex-1 overflow-y-auto p-4 flex flex-col lg:flex-row gap-6">
                <!-- FORM -->
                <div class="w-full lg:w-5/12 bg-slate-50 p-4 sm:p-5 rounded-2xl border flex flex-col h-fit shrink-0 space-y-3">
                    <h3 class="font-extrabold text-brand-dark border-b pb-2 text-base">Thêm / Sửa Dữ Liệu Xe</h3>
                    <input type="hidden" id="form-car-id">
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3.5">
                        <div><label class="block text-xs font-semibold text-gray-600 mb-1">Tên Xe</label><input type="text" id="form-car-name" class="w-full border rounded-lg p-2 text-sm outline-none"></div>
                        <div><label class="block text-xs font-semibold text-blue-700 mb-1">Tên chuẩn đối chiếu</label><input type="text" id="form-car-standard-name" list="standard-car-name-list" onchange="refreshCarColorImageManager()" oninput="refreshCarColorImageManager()" class="w-full border border-blue-200 rounded-lg p-2 text-sm outline-none" placeholder="Chọn hoặc nhập tên chuẩn"><datalist id="standard-car-name-list"></datalist></div>
                        <div><label class="block text-xs font-semibold text-gray-600 mb-1">Phiên Bản</label><input type="text" id="form-car-version" class="w-full border rounded-lg p-2 text-sm outline-none"></div>
                        <div><label class="block text-xs font-semibold text-gray-600 mb-1">Năm SX</label><input type="text" id="form-car-year" class="w-full border rounded-lg p-2 text-sm outline-none"></div>
                        <div><label class="block text-xs font-semibold text-gray-600 mb-1">Loại Xe</label><select id="form-car-type" class="w-full border rounded-lg p-2 text-sm outline-none bg-white"><option value="dulich">Du lịch</option><option value="bantai">Bán Tải</option></select></div>
                        <div><label class="block text-xs font-semibold text-gray-600 mb-1">Giá Niêm Yết</label><input type="text" inputmode="numeric" id="form-car-price" oninput="formatInputMoney(this)" class="w-full border rounded-lg p-2 text-sm outline-none text-right font-bold" placeholder="VD: 1.290.000.000"></div>
                        <div><label class="block text-xs font-semibold text-amber-700 mb-1">Mức giảm tối đa Nhà máy</label><input type="text" inputmode="numeric" id="form-car-cut-limit" oninput="formatInputMoney(this)" class="w-full border border-amber-300 rounded-lg p-2 text-sm outline-none font-bold text-amber-700 text-right" placeholder="VD: 50.000.000"></div>
                        <div><label class="block text-xs font-semibold text-rose-600 mb-1">Lương xe bán ra (Nội bộ)</label><input type="text" inputmode="numeric" id="form-car-sale-salary" oninput="formatInputMoney(this)" class="w-full border border-rose-300 rounded-lg p-2 text-sm outline-none font-bold text-rose-600 text-right" placeholder="VD: 15.000.000"></div>
                        
                        <div>
                            <label class="block text-xs font-semibold text-blue-600 mb-1">Gợi ý giảm thêm Đại lý</label>
                            <input type="text" inputmode="numeric" id="form-car-dealer-promo-suggest" oninput="formatInputMoney(this)" class="w-full border rounded-lg p-2 text-sm outline-none border-blue-300 font-bold text-blue-700 text-right" placeholder="VD: 20.000.000">
                        </div>
                        <div>
                            <label class="block text-xs font-semibold text-blue-600 mb-1">Gợi ý quà tặng Đại lý</label>
                            <textarea id="form-car-ctkm2-desc" rows="2" class="w-full border rounded-lg p-2 text-sm outline-none border-blue-200" placeholder="VD: Tặng BHVC 1 năm&#10;Tặng thảm sàn"></textarea>
                        </div>

                        <div class="col-span-1 sm:col-span-2">
                            <label class="block text-xs font-semibold text-blue-600 mb-1">Gợi ý Voucher Tri Ân</label>
                            <input type="text" id="form-car-voucher-desc" class="w-full border rounded-lg p-2 text-sm outline-none border-blue-200" placeholder="VD: Voucher Fadil 30 triệu">
                        </div>
                        <div class="col-span-1 sm:col-span-2">
                            <label class="block text-xs font-semibold text-emerald-700 mb-1">Nội dung Khuyến Mãi hiển thị trên báo giá</label>
                            <textarea id="form-car-promo-text" rows="3" class="w-full border border-emerald-300 rounded-lg p-2 text-sm outline-none bg-emerald-50/40" placeholder="Mỗi dòng là 1 nội dung khuyến mãi"></textarea>
                        </div>

                        <div><label class="block text-xs font-semibold text-gray-600 mb-1">Tỉ lệ BH Tặng (%)</label><input type="number" step="0.01" id="form-car-bh-tang" class="w-full border rounded-lg p-2 text-sm outline-none"></div>
                        <div><label class="block text-xs font-semibold text-gray-600 mb-1">Tỉ lệ BH Mua (%)</label><input type="number" step="0.01" id="form-car-bh-mua" class="w-full border rounded-lg p-2 text-sm outline-none"></div>
                        
                        <div>
                            <label class="block text-xs font-semibold text-violet-700 mb-1">Công suất tối đa</label>
                            <input type="text" id="form-car-max-power" class="w-full border border-violet-200 rounded-lg p-2 text-sm outline-none font-bold" placeholder="VD: 30 kW">
                        </div>
                        <div>
                            <label class="block text-xs font-semibold text-violet-700 mb-1">Dung lượng pin</label>
                            <input type="text" id="form-car-battery-capacity" class="w-full border border-violet-200 rounded-lg p-2 text-sm outline-none font-bold" placeholder="VD: 18,64 kWh">
                        </div>
                        <div class="col-span-1 sm:col-span-2">
                            <label class="block text-xs font-semibold text-violet-700 mb-1">Quãng đường di chuyển</label>
                            <input type="text" id="form-car-driving-range" class="w-full border border-violet-200 rounded-lg p-2 text-sm outline-none font-bold" placeholder="VD: ~210 km/lần sạc">
                        </div>

                        <div class="col-span-1 sm:col-span-2">
                            <label class="block text-xs font-semibold text-gray-600 mb-1">Ảnh xe mặc định</label>
                            <div class="grid grid-cols-1 sm:grid-cols-[1fr_auto] gap-2">
                                <input type="text" id="form-car-img" oninput="previewMainCarImageUrl()" class="w-full border rounded-lg p-2 text-sm outline-none" placeholder="Link ảnh hoặc dữ liệu ảnh Upload">
                                <label class="tactile-btn px-4 py-2 rounded-lg bg-blue-600 text-white text-xs font-black cursor-pointer flex items-center justify-center">
                                    Upload ảnh xe
                                    <input type="file" id="form-car-img-file" accept="image/*" class="hidden" onchange="uploadMainCarImage(this)">
                                </label>
                            </div>
                            <div class="mt-2 h-28 rounded-xl border bg-white flex items-center justify-center overflow-hidden">
                                <img id="form-car-img-preview" class="max-w-full max-h-28 object-contain" alt="Xem trước ảnh xe" onerror="this.style.opacity=.25" onload="this.style.opacity=1">
                            </div>
                        </div>

                        <!-- Color Images Manager -->
                        <div class="col-span-1 sm:col-span-2 rounded-xl border border-cyan-200 bg-cyan-50/70 p-3.5 space-y-2">
                            <div class="flex items-center justify-between gap-3">
                                <div>
                                    <div class="text-xs font-black text-cyan-900">Ảnh xe theo màu / Model</div>
                                    <div class="text-[9px] text-cyan-700">Chọn màu rồi Upload ảnh tương ứng</div>
                                </div>
                                <button type="button" onclick="refreshCarColorImageManager()" class="tactile-btn px-2.5 py-1 rounded-lg border border-cyan-300 bg-white text-cyan-700 text-[10px] font-black">Làm mới màu</button>
                            </div>
                            <input type="hidden" id="form-car-color-images-json" value="{{}}">
                            <div class="grid grid-cols-1 sm:grid-cols-[1fr_auto] gap-2">
                                <select id="form-car-color-image-select" onchange="previewSelectedCarColorImage()" class="w-full border rounded-lg p-2 text-sm bg-white"></select>
                                <label class="tactile-btn px-4 py-2 rounded-lg bg-cyan-600 text-white text-xs font-black cursor-pointer flex items-center justify-center">
                                    Upload màu
                                    <input type="file" id="form-car-color-image-file" accept="image/*" class="hidden" onchange="uploadSelectedCarColorImage(this)">
                                </label>
                            </div>
                            <div class="grid grid-cols-1 sm:grid-cols-[1fr_auto] gap-2">
                                <input type="url" id="form-car-color-image-url" oninput="previewCarColorImageUrlOnly()" onchange="saveSelectedCarColorImageUrl()" class="w-full border rounded-lg p-2 text-xs bg-white outline-none" placeholder="https://.../image.png">
                                <button type="button" onclick="saveSelectedCarColorImageUrl()" class="tactile-btn px-3 py-2 rounded-lg border border-cyan-300 bg-white text-cyan-700 text-[10px] font-black">Lưu link</button>
                            </div>
                            <div id="form-car-color-image-url-status" class="text-[9px] text-gray-500">Có thể dùng link ảnh trực tiếp</div>
                            <div class="h-28 rounded-xl border border-cyan-200 bg-white flex items-center justify-center overflow-hidden">
                                <img id="form-car-color-image-preview" class="max-w-full max-h-28 object-contain" alt="Ảnh màu xe" onload="handleCarColorPreviewLoad()" onerror="handleCarColorPreviewError()">
                                <span id="form-car-color-image-empty" class="text-[10px] text-gray-400">Chưa có ảnh riêng cho màu này</span>
                            </div>
                            <div class="flex justify-end">
                                <button type="button" onclick="removeSelectedCarColorImage()" class="tactile-btn px-3 py-1.5 rounded-lg bg-rose-50 border border-rose-200 text-rose-700 text-[10px] font-black">Xóa ảnh màu này</button>
                            </div>
                        </div>
                    </div>
                    <div><label class="block text-xs font-semibold text-gray-600 mb-1">Thông tin trang bị nổi bật</label><textarea id="form-car-specs" rows="3" class="w-full border rounded-lg p-2 text-xs outline-none"></textarea></div>
                    <div class="flex gap-2 pt-2">
                        <button onclick="saveCar()" class="tactile-btn flex-1 bg-emerald-600 hover:bg-emerald-700 text-white py-2.5 rounded-xl font-bold">Lưu Dữ Liệu</button>
                        <button onclick="clearCarForm()" class="tactile-btn px-5 bg-slate-200 hover:bg-slate-300 text-gray-800 rounded-xl font-bold">Tạo mới</button>
                    </div>
                </div>

                <!-- TABLE -->
                <div class="w-full lg:w-7/12 flex flex-col">
                    <div class="overflow-x-auto border rounded-2xl bg-white h-[400px] lg:h-[650px] custom-scrollbar shadow-sm">
                        <table class="w-full text-left text-sm text-gray-600 min-w-[500px]">
                            <thead class="bg-slate-100 text-gray-700 sticky top-0 z-10 shadow-sm font-bold text-xs"><tr><th class="p-3 w-16">Ảnh</th><th class="p-3">Tên Xe</th><th class="p-3">Giá Bán</th><th class="p-3 text-center">Xóa</th></tr></thead>
                            <tbody id="car-table-body" class="divide-y"></tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- 2. MODAL QUẢN LÝ PHỤ KIỆN -->
    <div id="accManagerModal" class="fixed inset-0 modal-backdrop-blur z-50 hidden justify-center items-center p-3 sm:p-5">
        <div class="bg-white w-full h-full sm:h-auto modal-content-box max-w-5xl max-h-full sm:max-h-[95vh] flex flex-col overflow-hidden">
            <div class="p-4 border-b flex justify-between items-center bg-slate-50 shrink-0">
                <div class="flex items-center gap-2">
                    <span class="text-xl">📦</span>
                    <h2 class="text-lg sm:text-xl font-bold text-gray-800">Danh Mục Phụ Kiện Chính Hãng</h2>
                </div>
                <button onclick="closeAccManager()" class="tactile-btn w-9 h-9 rounded-full bg-slate-200 text-gray-700 hover:text-red-600 text-2xl flex items-center justify-center leading-none">&times;</button>
            </div>
            <div class="flex-1 overflow-y-auto p-4 flex flex-col lg:flex-row gap-6">
                <!-- FORM -->
                <div class="w-full lg:w-1/3 bg-slate-50 p-4 sm:p-5 rounded-2xl border flex flex-col h-fit shrink-0 space-y-3.5">
                    <h3 class="font-extrabold text-brand-dark border-b pb-2 text-base">Thêm / Sửa Phụ Kiện</h3>
                    <input type="hidden" id="form-acc-id">
                    <div><label class="block text-xs font-semibold text-gray-600 mb-1">Loại Phụ Kiện</label><input type="text" id="form-acc-category" class="w-full border rounded-lg p-2 text-sm outline-none"></div>
                    <div><label class="block text-xs font-semibold text-gray-600 mb-1">Tên Phụ Kiện</label><input type="text" id="form-acc-name" class="w-full border rounded-lg p-2 text-sm outline-none"></div>
                    <div><label class="block text-xs font-semibold text-gray-600 mb-1">Giá trị Tặng (VNĐ)</label><input type="text" inputmode="numeric" id="form-acc-price-tang" oninput="formatInputMoney(this)" class="w-full border rounded-lg p-2 text-sm outline-none text-right font-bold"></div>
                    <div><label class="block text-xs font-semibold text-gray-600 mb-1">Giá trị Bán (VNĐ)</label><input type="text" inputmode="numeric" id="form-acc-price-mua" oninput="formatInputMoney(this)" class="w-full border rounded-lg p-2 text-sm outline-none text-right font-bold"></div>
                    <div class="flex gap-2 pt-2"><button onclick="saveAcc()" class="tactile-btn flex-1 bg-emerald-600 hover:bg-emerald-700 text-white py-2.5 rounded-xl font-bold">Lưu Dữ Liệu</button><button onclick="clearAccForm()" class="tactile-btn px-4 bg-slate-200 hover:bg-slate-300 text-gray-800 rounded-xl font-bold">Tạo mới</button></div>
                </div>
                <!-- BẢNG -->
                <div class="w-full lg:w-2/3 flex flex-col">
                    <div class="overflow-x-auto border rounded-2xl bg-white h-[400px] lg:h-[600px] custom-scrollbar shadow-sm">
                        <table class="w-full text-left text-sm text-gray-600 min-w-[600px]">
                            <thead class="bg-slate-100 text-gray-700 sticky top-0 z-10 shadow-sm font-bold text-xs"><tr><th class="p-3">Loại</th><th class="p-3">Tên Phụ Kiện</th><th class="p-3">Giá Tặng</th><th class="p-3">Giá Bán</th><th class="p-3 text-center">Xóa</th></tr></thead>
                            <tbody id="acc-table-body" class="divide-y"></tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- 3. MODAL QUẢN LÝ CTKM -->
    <div id="promoManagerModal" class="fixed inset-0 modal-backdrop-blur z-50 hidden justify-center items-center p-3 sm:p-5">
        <div class="bg-white w-full h-full sm:h-auto modal-content-box max-w-6xl max-h-full sm:max-h-[95vh] flex flex-col overflow-hidden">
            <div class="p-4 border-b flex justify-between items-center bg-slate-50 shrink-0">
                <div class="flex items-center gap-2">
                    <span class="text-xl">🎯</span>
                    <h2 class="text-lg sm:text-xl font-bold text-gray-800">Quản Lý Chương Trình Khuyến Mãi</h2>
                </div>
                <button onclick="closePromoManager()" class="tactile-btn w-9 h-9 rounded-full bg-slate-200 text-gray-700 hover:text-red-600 text-2xl flex items-center justify-center leading-none">&times;</button>
            </div>
            <div class="flex-1 overflow-y-auto p-4 flex flex-col lg:flex-row gap-6">
                <!-- FORM -->
                <div class="w-full lg:w-4/12 bg-slate-50 p-4 sm:p-5 rounded-2xl border flex flex-col h-fit shrink-0 space-y-3.5">
                    <h3 class="font-extrabold text-brand-dark border-b pb-2 text-base">Thêm / Sửa CTKM</h3>
                    <input type="hidden" id="form-promo-id">
                    <div>
                        <label class="block text-xs font-semibold text-gray-600 mb-1">Tên Chương Trình</label>
                        <input type="text" id="form-promo-name" class="w-full border rounded-lg p-2 text-sm outline-none" placeholder="VD: Vì Tương Lai Xanh, VinClub...">
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-gray-600 mb-1">Đối tượng / Điều kiện</label>
                        <input type="text" id="form-promo-target" class="w-full border rounded-lg p-2 text-sm outline-none" placeholder="VD: Hạng Gold, Khách có xe máy điện...">
                    </div>
                    <div>
                        <div class="flex items-center justify-between gap-2 mb-1">
                            <label class="block text-xs font-semibold text-blue-700">Xe áp dụng (Key chuẩn)</label>
                            <button type="button" onclick="toggleAllPromoCarKeys()" class="tactile-btn text-[10px] font-bold text-blue-700 bg-blue-50 border border-blue-200 px-2 py-0.5 rounded">Chọn tất cả</button>
                        </div>
                        <input type="hidden" id="form-promo-car-keys">
                        <div id="form-promo-car-key-options" class="max-h-40 overflow-y-auto border border-blue-200 rounded-lg bg-white p-2 grid grid-cols-1 sm:grid-cols-2 gap-1.5 custom-scrollbar"></div>
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-gray-600 mb-1">Phân Nhóm</label>
                        <select id="form-promo-group" class="w-full border rounded-lg p-2 text-sm outline-none font-bold text-indigo-700">
                            <option value="exclusive">Nhóm Đặc quyền (Chỉ được chọn 1)</option>
                            <option value="additive">Nhóm Bổ sung (Có thể chọn nhiều)</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-gray-600 mb-1">Hình thức Giảm</label>
                        <select id="form-promo-type" onchange="handlePromoTypeChange()" class="w-full border rounded-lg p-2 text-sm outline-none bg-white">
                            <option value="pct_msrp">% trên Giá Niêm Yết MSRP</option>
                            <option value="pct_after">% trên Giá Sau Khuyến Mãi (VD: Công vụ)</option>
                            <option value="money">Tiền mặt cố định (VND)</option>
                            <option value="custom">Nhập số tiền khi Báo giá (VD: Voucher)</option>
                        </select>
                    </div>
                    <div>
                        <label class="block text-xs font-semibold text-gray-600 mb-1">Mức giảm</label>
                        <input type="text" inputmode="decimal" id="form-promo-value" oninput="handlePromoValueInput(this)" class="w-full border rounded-lg p-2 text-sm outline-none font-bold text-right" placeholder="VD: 3 hoặc 30.000.000">
                    </div>
                    <div class="flex gap-2 pt-2">
                        <button onclick="savePromo()" class="tactile-btn flex-1 bg-fuchsia-600 hover:bg-fuchsia-700 text-white py-2.5 rounded-xl font-bold">Lưu Dữ Liệu</button>
                        <button onclick="clearPromoForm()" class="tactile-btn px-4 bg-slate-200 hover:bg-slate-300 text-gray-800 rounded-xl font-bold">Tạo mới</button>
                    </div>
                </div>
                <!-- BẢNG -->
                <div class="w-full lg:w-8/12 flex flex-col">
                    <div class="overflow-x-auto border rounded-2xl bg-white h-[400px] lg:h-[600px] custom-scrollbar shadow-sm">
                        <table class="w-full text-left text-sm text-gray-600 min-w-[700px]">
                            <thead class="bg-slate-100 text-gray-700 sticky top-0 z-10 shadow-sm font-bold text-xs"><tr><th class="p-3">Tên CTKM</th><th class="p-3">Dòng xe</th><th class="p-3">Đối tượng</th><th class="p-3">Mức giảm</th><th class="p-3">Phân nhóm</th><th class="p-3 text-center">Xóa</th></tr></thead>
                            <tbody id="promo-table-body" class="divide-y"></tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- 4. MODAL QUÀ TẶNG COMBO PHỤ KIỆN -->
    <div id="comboPickerModal" class="fixed inset-0 modal-backdrop-blur z-[100] hidden items-center justify-center p-3 sm:p-5">
        <div class="bg-white w-full max-w-3xl max-h-[92vh] modal-content-box overflow-hidden flex flex-col">
            <div class="p-4 border-b bg-indigo-50/80 flex items-start justify-between gap-3">
                <div class="flex items-center gap-2">
                    <span class="text-2xl">🎁</span>
                    <div>
                        <div class="text-base sm:text-lg font-black text-indigo-900 uppercase">Quà Tặng Combo Phụ Kiện</div>
                        <div id="combo-picker-subtitle" class="text-xs text-indigo-700 font-bold mt-0.5"></div>
                    </div>
                </div>
                <button onclick="closeComboPicker()" class="tactile-btn w-9 h-9 rounded-full bg-white border border-indigo-200 text-indigo-700 font-black flex items-center justify-center">✕</button>
            </div>

            <div id="combo-picker-list" class="p-4 overflow-y-auto flex-1 space-y-3.5 custom-scrollbar"></div>

            <div class="p-4 border-t bg-slate-50 flex flex-wrap justify-between gap-3 shrink-0">
                <button onclick="clearGiftAccessories(true)" class="tactile-btn px-4 py-2 bg-rose-50 text-rose-700 border border-rose-200 font-bold rounded-xl text-xs">Xóa toàn bộ PK tặng</button>
                <button onclick="closeComboPicker()" class="tactile-btn px-6 py-2 bg-slate-200 text-slate-800 font-bold rounded-xl text-xs">Đóng</button>
            </div>
        </div>
    </div>

    <!-- 5. MODAL PHỤ KIỆN BÁN CHO KHÁCH -->
    <div id="accPickerModal" class="fixed inset-0 modal-backdrop-blur z-50 hidden justify-center items-end sm:items-center p-0 sm:p-4">
        <div class="bg-white w-full sm:rounded-2xl modal-content-box max-w-4xl flex flex-col h-[90vh] sm:h-auto sm:max-h-[90vh] overflow-hidden">
            <div class="bg-purple-700 text-white px-5 py-4 flex items-center justify-between shrink-0">
                <div class="flex items-center gap-2.5">
                    <span class="text-xl">💳</span>
                    <div>
                        <h2 class="text-base sm:text-lg font-black uppercase">Phụ Kiện Bán Cho Khách</h2>
                        <p class="text-purple-200 text-xs mt-0.5" id="acc-picker-subtitle"></p>
                    </div>
                </div>
                <button onclick="closeAccPicker()" class="tactile-btn text-white text-3xl leading-none">&times;</button>
            </div>
            <div class="px-4 pt-3 bg-slate-50 border-b shrink-0">
                <div id="acc-sale-tabs" class="flex gap-2 overflow-x-auto pb-3 custom-scrollbar"></div>
            </div>
            <div class="overflow-x-auto bg-gray-50 flex-1 custom-scrollbar">
                <table class="w-full text-left bg-white min-w-[700px]">
                    <thead class="bg-slate-100 text-gray-700 text-xs uppercase font-bold sticky top-0 shadow-sm">
                        <tr><th class="p-3 pl-6">Tên Phụ Kiện</th><th class="p-3 w-40 text-center">Hình thức</th><th class="p-3 w-[280px]">Tùy chỉnh giá Mua</th></tr>
                    </thead>
                    <tbody id="acc-picker-list" class="divide-y text-sm"></tbody>
                </table>
            </div>
            <div class="p-4 bg-slate-50 border-t flex flex-wrap justify-end gap-3 shrink-0">
                <button onclick="clearPurchasedAccessories(true)" class="tactile-btn px-5 py-2.5 bg-rose-50 text-rose-700 border border-rose-200 font-bold rounded-xl text-xs">Xóa PK mua</button>
                <button onclick="closeAccPicker()" class="tactile-btn px-5 py-2.5 bg-slate-200 text-slate-800 font-bold rounded-xl text-xs">Hủy</button>
                <button onclick="saveAccPicker()" class="tactile-btn px-6 py-2.5 bg-purple-600 hover:bg-purple-700 text-white font-bold rounded-xl text-xs">Lưu vào Báo giá</button>
            </div>
        </div>
    </div>

    <!-- 6. MODAL COPY TEXT -->
    <div id="quoteInfoModal" class="fixed inset-0 modal-backdrop-blur z-50 hidden justify-center items-end sm:items-center p-0 sm:p-4">
        <div class="bg-white w-full sm:rounded-2xl modal-content-box max-w-xl flex flex-col h-[85vh] sm:h-auto overflow-hidden">
            <div class="bg-emerald-600 text-white px-6 py-4 flex items-center justify-between shrink-0">
                <div class="flex items-center gap-2">
                    <span class="text-xl">📋</span>
                    <h2 class="text-lg font-bold">Thông Tin Báo Giá Dạng Text</h2>
                </div>
                <button onclick="closeQuoteInfo()" class="tactile-btn text-3xl leading-none">&times;</button>
            </div>
            <div class="p-6 overflow-y-auto space-y-4">
                <div id="quoteInfoSummary" class="border rounded-xl p-3.5 bg-emerald-50/50"></div>
                <div><textarea id="quoteInfoText" readonly class="w-full h-44 border rounded-xl p-3 text-xs sm:text-sm bg-slate-50 outline-none font-mono"></textarea></div>
                <div class="flex gap-3">
                    <button onclick="copyQuoteInfo()" id="copyQuoteInfoBtn" class="tactile-btn flex-1 bg-emerald-600 hover:bg-emerald-700 text-white py-3 rounded-xl font-bold text-sm">Sao chép văn bản</button>
                    <button onclick="closeQuoteInfo()" class="tactile-btn px-6 bg-slate-200 hover:bg-slate-300 text-gray-800 py-3 rounded-xl font-bold text-sm">Đóng</button>
                </div>
            </div>
        </div>
    </div>

    <!-- 7. MODAL MỐC BẢO DƯỠNG -->
    <div id="maintenanceModal" class="fixed inset-0 modal-backdrop-blur z-[70] hidden flex-col items-center justify-center p-3 sm:p-6">
        <div class="w-full max-w-[680px] max-h-[92vh] bg-white modal-content-box overflow-hidden flex flex-col">
            <div class="px-5 py-4 border-b bg-slate-50 flex items-start justify-between gap-4 shrink-0">
                <div class="min-w-0">
                    <div class="text-lg sm:text-xl font-black text-gray-900 flex items-center gap-2">
                        <span>🔧</span><span>Mốc Bảo Dưỡng Định Kỳ</span>
                    </div>
                    <div id="maintenance-model-title" class="text-xs sm:text-sm font-black text-blue-700 mt-1">—</div>
                    <div id="maintenance-source-note" class="text-[10px] text-gray-500 mt-0.5">—</div>
                </div>
                <button type="button" onclick="closeMaintenanceSchedule()" class="tactile-btn w-9 h-9 rounded-full bg-slate-800 text-white text-xl font-black shrink-0 flex items-center justify-center">×</button>
            </div>
            <div class="flex-1 overflow-auto p-5 bg-slate-50 space-y-3 custom-scrollbar">
                <div id="maintenance-summary-wrap" class="space-y-2.5"></div>
                <div id="maintenance-footnote" class="text-[10px] text-gray-500 leading-relaxed pt-2"></div>
            </div>
        </div>
    </div>

    <!-- 8. MODAL PREVIEW & EXPORT -->
    <div id="previewModal" class="fixed inset-0 bg-slate-950/95 z-50 hidden flex-col items-center pt-6 pb-4">
        <div class="w-[1024px] max-w-[100vw] flex flex-col gap-3 md:flex-row md:justify-between md:items-center text-white mb-4 px-4 shrink-0">
            <div>
                <h2 class="text-xl sm:text-2xl font-display font-extrabold flex items-center gap-2">
                    <span>📸</span><span>Xem Trước Báo Giá Xuất Ảnh</span>
                </h2>
                <div class="text-[11px] text-slate-300 mt-0.5">Khổ in 1024px chuẩn HD sắc nét. Bạn có thể xuất toàn bộ báo giá hoặc phần giữa.</div>
            </div>
            <div class="flex flex-wrap gap-2">
                <button onclick="closePreview()" class="tactile-btn bg-slate-700 hover:bg-slate-600 px-4 py-2 rounded-xl font-bold text-xs">Đóng</button>
                <button onclick="savePreviewImage('full', this)" id="save-image-btn" class="tactile-btn bg-brand-primary hover:bg-blue-600 px-5 py-2 rounded-xl font-black text-xs shadow-lg shadow-blue-500/30">Lưu Hình HD</button>
                <button onclick="savePreviewPdf('full', this)" id="save-pdf-btn" class="tactile-btn bg-rose-600 hover:bg-rose-500 px-4 py-2 rounded-xl font-black text-xs shadow-lg shadow-rose-600/30">Xuất PDF</button>
                <button onclick="savePreviewImage('focus', this)" id="save-image-focus-btn" class="tactile-btn bg-cyan-600 hover:bg-cyan-500 px-3.5 py-2 rounded-xl font-black text-xs">Lưu phần giữa</button>
                <button onclick="savePreviewPdf('focus', this)" id="save-pdf-focus-btn" class="tactile-btn bg-amber-600 hover:bg-amber-500 px-3.5 py-2 rounded-xl font-black text-xs">PDF phần giữa</button>
            </div>
        </div>
        <div id="preview-scroll-container" class="flex-1 w-full overflow-y-auto overflow-x-auto flex justify-center pb-12 custom-scrollbar">
            <div id="preview-container" class="shadow-2xl rounded-2xl origin-top" style="transform: scale(0.85); margin-top: 10px;"></div>
        </div>
    </div>

    <!-- ================= JAVASCRIPT CORE & LOGIC ================= -->
    <script>
{core_js}
    </script>

    <!-- ================= JAVASCRIPT MOTION & INTERACTION LAYER ================= -->
    <script>
{motion_layer_js}
    </script>
</body>
</html>
"""

with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
    f.write(html_template)

print("Generated clean modernized index.html successfully!")
print("Output size:", os.path.getsize(OUTPUT_PATH))
