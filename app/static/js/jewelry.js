// Jewelry & Outfit Vision Frontend Logic

let currentJewelryData = null;
let currentCurrency = '$';
let selectedFile = null;

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('jewelry-form');
    const budgetInput = document.getElementById('budget');
    const budgetDisplay = document.getElementById('budget-display');
    const presetBtns = document.querySelectorAll('.preset-btn');
    
    // Dropzone elements
    const dropzone = document.getElementById('dropzone');
    const fileInput = document.getElementById('outfit_image');
    const dropzonePrompt = document.getElementById('dropzone-prompt');
    const dropzonePreview = document.getElementById('dropzone-preview');
    const previewImg = document.getElementById('preview-img');
    const previewFilename = document.getElementById('preview-filename');
    const removeImgBtn = document.getElementById('remove-img-btn');

    // Preset buttons
    presetBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const amount = btn.getAttribute('data-amount');
            budgetInput.value = amount;
            updateBudgetDisplay(amount);
        });
    });

    budgetInput.addEventListener('input', (e) => {
        updateBudgetDisplay(e.target.value);
    });

    function updateBudgetDisplay(val) {
        budgetDisplay.textContent = `${currentCurrency}${Number(val).toLocaleString()}`;
    }

    // Dropzone Click & Drag/Drop
    dropzone.addEventListener('click', (e) => {
        if (e.target.closest('#remove-img-btn')) return;
        fileInput.click();
    });

    fileInput.addEventListener('change', (e) => {
        if (e.target.files && e.target.files[0]) {
            handleImageFile(e.target.files[0]);
        }
    });

    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
    });

    dropzone.addEventListener('dragleave', () => {
        dropzone.classList.remove('dragover');
    });

    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleImageFile(e.dataTransfer.files[0]);
        }
    });

    function handleImageFile(file) {
        selectedFile = file;
        const reader = new FileReader();
        reader.onload = (event) => {
            previewImg.src = event.target.result;
            previewFilename.textContent = file.name;
            dropzonePrompt.classList.add('hidden');
            dropzonePreview.classList.remove('hidden');
            showToast('Outfit image loaded for AI vision inspection', 'success');
        };
        reader.readAsDataURL(file);
    }

    removeImgBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        selectedFile = null;
        fileInput.value = '';
        previewImg.src = '';
        dropzonePreview.classList.add('hidden');
        dropzonePrompt.classList.remove('hidden');
    });

    // Form Submit
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const occasion = document.getElementById('occasion').value;
        const necklineOutfit = document.getElementById('neckline_outfit').value;
        const metalPref = document.getElementById('metal_preference').value;
        const gemstonePref = document.getElementById('gemstone_preference').value;
        const clothingColor = document.getElementById('clothing_color').value;
        const budget = parseFloat(budgetInput.value);

        // UI states
        document.getElementById('placeholder-box').classList.add('hidden');
        document.getElementById('plan-output').classList.add('hidden');
        document.getElementById('loading-box').classList.remove('hidden');

        const formData = new FormData();
        formData.append('occasion', occasion);
        formData.append('neckline_outfit', necklineOutfit);
        formData.append('metal_preference', metalPref);
        formData.append('gemstone_preference', gemstonePref);
        formData.append('clothing_color', clothingColor);
        formData.append('budget', budget);
        formData.append('currency', currentCurrency);

        if (selectedFile) {
            formData.append('outfit_image', selectedFile);
        }

        try {
            const response = await fetch('/api/jewelry/generate', {
                method: 'POST',
                body: formData
            });

            if (response.status === 401) {
                window.location.href = `/login?next=${encodeURIComponent(window.location.pathname)}`;
                return;
            }

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'Failed to curate jewelry plan');
            }

            const data = await response.json();
            currentJewelryData = data.plan;
            renderJewelryPlan(data.plan, budget, data.image_url);
            showToast('Jewelry Curation & Outfit Vision complete!', 'success');

        } catch (err) {
            console.error(err);
            showToast(err.message || 'Error communicating with AI service', 'error');
            document.getElementById('placeholder-box').classList.remove('hidden');
        } finally {
            document.getElementById('loading-box').classList.add('hidden');
        }
    });

    // Tier switching
    const tierThrifty = document.getElementById('tier-btn-thrifty');
    const tierBalanced = document.getElementById('tier-btn-balanced');
    const tierLuxe = document.getElementById('tier-btn-luxe');

    if (tierThrifty && tierBalanced && tierLuxe) {
        tierThrifty.addEventListener('click', () => switchJewelryTier('thrifty'));
        tierBalanced.addEventListener('click', () => switchJewelryTier('balanced'));
        tierLuxe.addEventListener('click', () => switchJewelryTier('luxe'));
    }

    // Copy Summary button
    const copyBtn = document.getElementById('copy-summary-btn');
    if (copyBtn) {
        copyBtn.addEventListener('click', () => {
            if (!currentJewelryData) return;
            const set = currentJewelryData.curated_set || {};
            const text = `${currentJewelryData.title}\nBudget: ${currentCurrency}${currentJewelryData.total_allocated}\n\nSuite:\n- Primary: ${set.primary_piece?.name || ''} (${currentCurrency}${set.primary_piece?.est_cost || 0})\n- Earrings: ${set.earrings?.name || ''} (${currentCurrency}${set.earrings?.est_cost || 0})\n- Wrist: ${set.wrist_piece?.name || ''} (${currentCurrency}${set.wrist_piece?.est_cost || 0})\n- Ring: ${set.finger_piece?.name || ''} (${currentCurrency}${set.finger_piece?.est_cost || 0})\n\nGuidance: ${currentJewelryData.outfit_analysis?.neckline_guidance || ''}`;
            copyText(text, 'Jewelry curation copied to clipboard!');
        });
    }
});

function renderJewelryPlan(plan, budget, imageUrl) {
    document.getElementById('plan-output').classList.remove('hidden');

    document.getElementById('plan-title').textContent = plan.title;
    document.getElementById('plan-budget').textContent = `${currentCurrency}${Number(budget).toLocaleString()}`;

    // Outfit Analysis
    const analysis = plan.outfit_analysis || {};
    document.getElementById('outfit-detected-style').textContent = analysis.detected_style || 'Form-fitting tailored evening silhouette';
    document.getElementById('outfit-color-harmony').textContent = analysis.color_harmony || 'Warm metallic luster complements deep fabric saturation';
    document.getElementById('outfit-neckline-guidance').textContent = analysis.neckline_guidance || 'Balances focal weight cleanly against collar lines';

    // Show image container if image was uploaded or returned
    const imgContainer = document.getElementById('outfit-image-container');
    const analyzedImg = document.getElementById('outfit-analyzed-img');
    if (imageUrl) {
        analyzedImg.src = imageUrl;
        imgContainer.classList.remove('hidden');
    } else if (previewImg && previewImg.src && !previewImg.src.includes('window.location')) {
        analyzedImg.src = previewImg.src;
        imgContainer.classList.remove('hidden');
    } else {
        imgContainer.classList.add('hidden');
    }

    // Curated 4-Piece Suite
    const set = plan.curated_set || {};
    
    // Primary piece
    const p = set.primary_piece || {};
    document.getElementById('set-p-cat').textContent = p.category || 'Focal Statement';
    document.getElementById('set-p-name').textContent = p.name || 'Statement Piece';
    document.getElementById('set-p-cost').textContent = `${currentCurrency}${Number(p.est_cost || 0).toLocaleString()}`;
    document.getElementById('set-p-role').textContent = p.styling_role || '';
    document.getElementById('set-p-metal').textContent = p.metal || '';
    document.getElementById('set-p-gem').textContent = p.gemstones || '';

    // Earrings
    const e = set.earrings || {};
    document.getElementById('set-e-name').textContent = e.name || 'Coordinated Earrings';
    document.getElementById('set-e-cost').textContent = `${currentCurrency}${Number(e.est_cost || 0).toLocaleString()}`;
    document.getElementById('set-e-role').textContent = e.styling_role || '';
    document.getElementById('set-e-metal').textContent = e.metal || '';
    document.getElementById('set-e-gem').textContent = e.gemstones || '';

    // Wrist
    const w = set.wrist_piece || {};
    document.getElementById('set-w-name').textContent = w.name || 'Wrist Bangle / Bracelet';
    document.getElementById('set-w-cost').textContent = `${currentCurrency}${Number(w.est_cost || 0).toLocaleString()}`;
    document.getElementById('set-w-role').textContent = w.styling_role || '';
    document.getElementById('set-w-metal').textContent = w.metal || '';
    document.getElementById('set-w-gem').textContent = w.gemstones || '';

    // Ring
    const r = set.finger_piece || {};
    document.getElementById('set-r-name').textContent = r.name || 'Accent Cocktail Ring';
    document.getElementById('set-r-cost').textContent = `${currentCurrency}${Number(r.est_cost || 0).toLocaleString()}`;
    document.getElementById('set-r-role').textContent = r.styling_role || '';
    document.getElementById('set-r-metal').textContent = r.metal || '';
    document.getElementById('set-r-gem').textContent = r.gemstones || '';

    // Chart.js Donut
    const labels = (plan.budget_breakdown || []).map(b => b.category);
    const amounts = (plan.budget_breakdown || []).map(b => b.allocated_amount);
    renderBudgetChart('jewelryChart', labels, amounts, ['#f59e0b', '#10b981', '#6366f1', '#ec4899']);

    // Default tier
    switchJewelryTier('balanced');

    // Rules
    const rulesList = document.getElementById('rules-list');
    rulesList.innerHTML = '';
    (plan.styling_rules || []).forEach(rule => {
        const li = document.createElement('li');
        li.className = 'flex items-start gap-2';
        li.innerHTML = `<i data-lucide="sparkles" class="w-3.5 h-3.5 text-amber-500 flex-shrink-0 mt-0.5"></i><span>${rule}</span>`;
        rulesList.appendChild(li);
    });

    // Hacks
    const hacksList = document.getElementById('hacks-list');
    hacksList.innerHTML = '';
    (plan.cost_saving_hacks || []).forEach(hack => {
        const li = document.createElement('li');
        li.className = 'flex items-start gap-2';
        li.innerHTML = `<i data-lucide="lightbulb" class="w-3.5 h-3.5 text-emerald-500 flex-shrink-0 mt-0.5"></i><span>${hack}</span>`;
        hacksList.appendChild(li);
    });

    lucide.createIcons();
}

function switchJewelryTier(tierKey) {
    if (!currentJewelryData || !currentJewelryData.tiers) return;
    const tier = currentJewelryData.tiers[tierKey];
    if (!tier) return;

    ['thrifty', 'balanced', 'luxe'].forEach(key => {
        const btn = document.getElementById(`tier-btn-${key}`);
        if (btn) {
            if (key === tierKey) {
                btn.className = 'tier-tab-btn py-2 rounded-lg bg-white text-amber-700 shadow-xs transition-all text-center font-bold';
            } else {
                btn.className = 'tier-tab-btn py-2 rounded-lg text-slate-600 hover:text-slate-900 transition-all text-center';
            }
        }
    });

    document.getElementById('tier-title').textContent = tier.label;
    document.getElementById('tier-cost').textContent = `${currentCurrency}${Number(tier.total).toLocaleString()}`;
    document.getElementById('tier-strategy').textContent = tier.strategy;

    const choicesList = document.getElementById('tier-choices');
    choicesList.innerHTML = '';
    (tier.key_choices || []).forEach(choice => {
        const li = document.createElement('li');
        li.className = 'flex items-start gap-1.5';
        li.innerHTML = `<i data-lucide="arrow-right" class="w-3.5 h-3.5 text-amber-600 flex-shrink-0 mt-0.5"></i><span>${choice}</span>`;
        choicesList.appendChild(li);
    });

    lucide.createIcons({ root: choicesList });
}
