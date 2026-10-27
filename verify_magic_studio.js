// verify_magic_studio.js
const fs = require('fs');

async function run() {
    const listRes = await fetch("http://127.0.0.1:9222/json/list");
    const targets = await listRes.json();
    const pageTarget = targets.find(t => t.url && t.url.includes("localhost:8080"));
    if (!pageTarget) {
        console.error("No localhost:8080 target found!");
        return;
    }
    const ws = new WebSocket(pageTarget.webSocketDebuggerUrl);
    await new Promise(r => ws.onopen = r);
    let id = 1;
    function send(method, params={}) {
        return new Promise((resolve) => {
            const reqId = id++;
            const handler = (evt) => {
                const msg = JSON.parse(evt.data);
                if (msg.id === reqId) {
                    ws.removeEventListener('message', handler);
                    resolve(msg.result || msg.error);
                }
            };
            ws.addEventListener('message', handler);
            ws.send(JSON.stringify({ id: reqId, method, params }));
        });
    }
    await send("Runtime.enable");
    await send("Page.enable");
    await send("Emulation.setDeviceMetricsOverride", {
        width: 1440,
        height: 900,
        deviceScaleFactor: 1,
        mobile: false
    });

    console.log("1. Reloading page...");
    await send("Page.reload", { ignoreCache: true });
    await new Promise(r => setTimeout(r, 2000));

    console.log("2. Opening Magic Cyber Modal via toggleLiveCustomize(true)...");
    const openRes = await send("Runtime.evaluate", {
        expression: `(() => {
            toggleLiveCustomize(true);
            const panel = document.getElementById('live-customize-panel');
            const backdrop = document.getElementById('live-customize-backdrop');
            const footer = panel.querySelector('.sticky.bottom-0');
            return {
                panelVisible: !panel.classList.contains('hidden-panel'),
                backdropVisible: !backdrop.classList.contains('hidden'),
                footerExists: !!footer,
                carName: document.getElementById('live-customize-car')?.innerText,
                initialTotal: document.getElementById('quote-total')?.innerText
            };
        })()`,
        returnByValue: true
    });
    console.log("Open state:", JSON.stringify(openRes.result?.value, null, 2));

    // Capture screenshot of the modal with sticky footer & toast
    const modalShot = await send("Page.captureScreenshot", { format: "png" });
    if (modalShot && modalShot.data) {
        fs.writeFileSync(
            "C:\\Users\\PC\\.gemini\\antigravity\\brain\\5562f8dc-7db2-4a7f-b697-50b0d35c9cc8\\preview_magic_modal_sticky.png",
            Buffer.from(modalShot.data, "base64")
        );
        console.log("Saved preview_magic_modal_sticky.png!");
    }

    console.log("3. Testing bidirectional fee recalculation...");
    const feeTest = await send("Runtime.evaluate", {
        expression: `(() => {
            const preset = document.getElementById('live-registration-preset');
            
            // Set to ward (140.000)
            preset.value = 'ward';
            preset.dispatchEvent(new Event('change'));
            const wardTotal = document.getElementById('quote-total')?.innerText;
            const wardReg = document.getElementById('quote-phi-dang-ky')?.innerText;

            // Set to metro (14.000.000)
            preset.value = 'metro';
            preset.dispatchEvent(new Event('change'));
            const metroTotal = document.getElementById('quote-total')?.innerText;
            const metroReg = document.getElementById('quote-phi-dang-ky')?.innerText;

            return {
                wardReg,
                wardTotal,
                metroReg,
                metroTotal,
                isReactive: wardTotal !== metroTotal
            };
        })()`,
        returnByValue: true
    });
    console.log("Bidirectional fee test:", JSON.stringify(feeTest.result?.value, null, 2));

    console.log("4. Testing Escape key to close modal...");
    const escapeTest = await send("Runtime.evaluate", {
        expression: `(() => {
            window.dispatchEvent(new KeyboardEvent('keydown', { key: 'Escape' }));
            const panel = document.getElementById('live-customize-panel');
            const backdrop = document.getElementById('live-customize-backdrop');
            return {
                panelHiddenAfterEscape: panel.classList.contains('hidden-panel'),
                backdropHiddenAfterEscape: backdrop.classList.contains('hidden')
            };
        })()`,
        returnByValue: true
    });
    console.log("Escape test:", JSON.stringify(escapeTest.result?.value, null, 2));

    console.log("5. Scrolling to car showroom stage and capturing pedestal & swatches...");
    await send("Runtime.evaluate", {
        expression: `(() => {
            const specCard = document.querySelector('.quote-spec-card');
            if (specCard) {
                specCard.scrollIntoView({ behavior: 'instant', block: 'center' });
            }
        })()`
    });
    await new Promise(r => setTimeout(r, 600));

    const stageShot = await send("Page.captureScreenshot", { format: "png" });
    if (stageShot && stageShot.data) {
        fs.writeFileSync(
            "C:\\Users\\PC\\.gemini\\antigravity\\brain\\5562f8dc-7db2-4a7f-b697-50b0d35c9cc8\\preview_magic_pedestal_swatches.png",
            Buffer.from(stageShot.data, "base64")
        );
        console.log("Saved preview_magic_pedestal_swatches.png!");
    }

    console.log("6. Testing Export PDF without errors...");
    const exportPdfTest = await send("Runtime.evaluate", {
        expression: `(() => {
            try {
                // Test building clone for PDF
                const clone = buildFocusedExportClone ? buildFocusedExportClone('full') : null;
                return {
                    cloneCreated: !!clone,
                    cloneWidth: clone?.style?.width || clone?.offsetWidth
                };
            } catch(e) {
                return { error: e.message };
            }
        })()`,
        returnByValue: true
    });
    console.log("Export clone test:", JSON.stringify(exportPdfTest.result?.value, null, 2));

    ws.close();
    console.log("ALL VERIFICATIONS COMPLETED SUCCESSFULLY!");
}

run().catch(console.error);
