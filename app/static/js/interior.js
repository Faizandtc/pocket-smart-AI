// Interior Planner Frontend Logic

let currentPlanData = null;
let currentCurrency = '$';

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('interior-form');
    const budgetInput = document.getElementById('budget');
    const budgetDisplay = document.getElementById('budget-display');
    const presetBtns = document.querySelectorAll('.preset-btn');

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

    // Form submission
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const roomType = document.getElementById('room_type').value;
        const style = document.getElementById('style').value;
        const dimensions = document.getElementById('dimensions').value;
        const targetPalette = document.getElementById('target_palette').value;
        const budget = parseFloat(budgetInput.value);
        const specialRequirements = document.getElementById('special_requirements').value;

        // UI states
        document.getElementById('placeholder-box').classList.add('hidden');
        document.getElementById('plan-output').classList.add('hidden');
        document.getElementById('loading-box').classList.remove('hidden');

        try {
            const response = await fetch('/api/interior/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    room_type: roomType,
                    style: style,
                    dimensions: dimensions,
                    target_palette: targetPalette,
                    budget: budget,
                    currency: currentCurrency,
                    special_requirements: specialRequirements
                })
            });

            if (response.status === 401) {
                // Not authenticated
                window.location.href = `/login?next=${encodeURIComponent(window.location.pathname)}`;
                return;
            }

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'Failed to generate plan');
            }

            const data = await response.json();
            currentPlanData = data.plan;
            renderInteriorPlan(data.plan, budget);
            showToast('Interior Plan generated and saved!', 'success');

        } catch (err) {
            console.error(err);
            showToast(err.message || 'Error communicating with AI service', 'error');
            document.getElementById('placeholder-box').classList.remove('hidden');
        } finally {
            document.getElementById('loading-box').classList.add('hidden');
        }
    });

    // Tier switcher event handlers
    const tierThrifty = document.getElementById('tier-btn-thrifty');
    const tierBalanced = document.getElementById('tier-btn-balanced');
    const tierLuxe = document.getElementById('tier-btn-luxe');

    if (tierThrifty && tierBalanced && tierLuxe) {
        tierThrifty.addEventListener('click', () => switchTier('thrifty'));
        tierBalanced.addEventListener('click', () => switchTier('balanced'));
        tierLuxe.addEventListener('click', () => switchTier('luxe'));
    }

    // Copy Summary button
    const copyBtn = document.getElementById('copy-summary-btn');
    if (copyBtn) {
        copyBtn.addEventListener('click', () => {
            if (!currentPlanData) return;
            const text = `${currentPlanData.title}\nBudget: ${currentCurrency}${currentPlanData.total_allocated}\n\nSummary:\n${currentPlanData.summary}\n\nKey Strategy:\n${currentPlanData.tiers?.balanced?.strategy || ''}`;
            copyText(text, 'Plan summary copied to clipboard!');
        });
    }
});

function renderInteriorPlan(plan, budget) {
    document.getElementById('plan-output').classList.remove('hidden');

    document.getElementById('plan-title').textContent = plan.title;
    document.getElementById('plan-summary').textContent = plan.summary;
    document.getElementById('plan-budget').textContent = `${currentCurrency}${Number(budget).toLocaleString()}`;

    // Render Color Palette
    const paletteGrid = document.getElementById('palette-grid');
    paletteGrid.innerHTML = '';
    (plan.color_palette || []).forEach(color => {
        const swatch = document.createElement('div');
        swatch.className = 'palette-swatch shadow-xs';
        swatch.style.backgroundColor = color.hex;
        
        // Determine text color for contrast
        const isLight = isColorLight(color.hex);
        swatch.style.color = isLight ? '#0f172a' : '#ffffff';
        
        swatch.innerHTML = `
            <span class="font-bold truncate text-[11px]">${color.name}</span>
            <span class="text-[9px] opacity-80 uppercase">${color.role || ''} (${color.hex})</span>
        `;
        paletteGrid.appendChild(swatch);
    });

    // Render Chart.js Donut
    const labels = (plan.budget_breakdown || []).map(b => b.category);
    const amounts = (plan.budget_breakdown || []).map(b => b.allocated_amount);
    renderBudgetChart('interiorChart', labels, amounts, ['#10b981', '#3b82f6', '#f59e0b', '#8b5cf6', '#64748b']);

    // Render Default Tier (Balanced)
    switchTier('balanced');

    // Render Itemized Tables
    const tablesContainer = document.getElementById('breakdown-tables-container');
    tablesContainer.innerHTML = '';
    (plan.budget_breakdown || []).forEach(cat => {
        const catCard = document.createElement('div');
        catCard.className = 'border border-slate-200 rounded-xl overflow-hidden bg-slate-50/50';

        let itemsHtml = (cat.items || []).map(item => `
            <tr class="border-b border-slate-100 hover:bg-white text-xs">
                <td class="p-3 font-semibold text-slate-800">${item.name}</td>
                <td class="p-3 text-slate-500 hidden sm:table-cell">${item.shopping_tip || '-'}</td>
                <td class="p-3 text-center">
                    <span class="px-2 py-0.5 rounded-full text-[10px] font-bold ${
                        item.priority === 'Must-Have' ? 'bg-emerald-100 text-emerald-800' : 'bg-slate-200 text-slate-700'
                    }">${item.priority || 'Standard'}</span>
                </td>
                <td class="p-3 text-right font-mono font-bold text-slate-900">${currentCurrency}${Number(item.est_cost).toLocaleString()}</td>
            </tr>
        `).join('');

        catCard.innerHTML = `
            <div class="px-4 py-2.5 bg-slate-100/90 flex justify-between items-center text-xs font-bold text-slate-700 border-b border-slate-200">
                <span>${cat.category} (${cat.percentage}%)</span>
                <span class="font-mono text-emerald-700">${currentCurrency}${Number(cat.allocated_amount).toLocaleString()}</span>
            </div>
            <table class="w-full text-left">
                <thead>
                    <tr class="text-[10px] uppercase tracking-wider text-slate-400 bg-slate-50/80 border-b border-slate-200">
                        <th class="p-3">Piece / Item</th>
                        <th class="p-3 hidden sm:table-cell">Sourcing & Material Advice</th>
                        <th class="p-3 text-center">Priority</th>
                        <th class="p-3 text-right">Est. Cost</th>
                    </tr>
                </thead>
                <tbody>${itemsHtml}</tbody>
            </table>
        `;
        tablesContainer.appendChild(catCard);
    });

    // Spatial advice
    const spatialList = document.getElementById('spatial-list');
    spatialList.innerHTML = '';
    (plan.spatial_advice || []).forEach(tip => {
        const li = document.createElement('li');
        li.className = 'flex items-start gap-2';
        li.innerHTML = `<i data-lucide="check" class="w-3.5 h-3.5 text-blue-500 flex-shrink-0 mt-0.5"></i><span>${tip}</span>`;
        spatialList.appendChild(li);
    });

    // Cost hacks
    const hacksList = document.getElementById('hacks-list');
    hacksList.innerHTML = '';
    (plan.cost_saving_hacks || []).forEach(hack => {
        const li = document.createElement('li');
        li.className = 'flex items-start gap-2';
        li.innerHTML = `<i data-lucide="sparkles" class="w-3.5 h-3.5 text-amber-500 flex-shrink-0 mt-0.5"></i><span>${hack}</span>`;
        hacksList.appendChild(li);
    });

    lucide.createIcons();
}

function switchTier(tierKey) {
    if (!currentPlanData || !currentPlanData.tiers) return;
    const tier = currentPlanData.tiers[tierKey];
    if (!tier) return;

    // Toggle button styles
    ['thrifty', 'balanced', 'luxe'].forEach(key => {
        const btn = document.getElementById(`tier-btn-${key}`);
        if (btn) {
            if (key === tierKey) {
                btn.className = 'tier-tab-btn py-2 rounded-lg bg-white text-emerald-700 shadow-xs transition-all text-center font-bold';
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
        li.innerHTML = `<i data-lucide="arrow-right" class="w-3.5 h-3.5 text-emerald-600 flex-shrink-0 mt-0.5"></i><span>${choice}</span>`;
        choicesList.appendChild(li);
    });

    lucide.createIcons({ root: choicesList });
}

function isColorLight(hex) {
    hex = hex.replace('#', '');
    if (hex.length === 3) hex = hex.split('').map(c => c + c).join('');
    const r = parseInt(hex.substr(0, 2), 16);
    const g = parseInt(hex.substr(2, 2), 16);
    const b = parseInt(hex.substr(4, 2), 16);
    const brightness = (r * 299 + g * 587 + b * 114) / 1000;
    return brightness > 155;
}
