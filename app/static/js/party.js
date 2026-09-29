// Party Planner Frontend Logic

let currentPartyData = null;
let currentCurrency = '$';

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('party-form');
    const budgetInput = document.getElementById('budget');
    const budgetDisplay = document.getElementById('budget-display');
    const guestSlider = document.getElementById('guest_count');
    const guestCountVal = document.getElementById('guest-count-val');
    const perGuestIndicator = document.getElementById('per-guest-indicator');
    const presetBtns = document.querySelectorAll('.preset-btn');

    function updateCalculations() {
        const budget = parseFloat(budgetInput.value) || 0;
        const guests = parseInt(guestSlider.value) || 1;
        
        budgetDisplay.textContent = `${currentCurrency}${budget.toLocaleString()}`;
        guestCountVal.textContent = `${guests} Guests`;
        
        const perGuest = Math.round((budget / guests) * 100) / 100;
        perGuestIndicator.textContent = `${currentCurrency}${perGuest.toFixed(2)} / guest`;
    }

    presetBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            budgetInput.value = btn.getAttribute('data-amount');
            updateCalculations();
        });
    });

    budgetInput.addEventListener('input', updateCalculations);
    guestSlider.addEventListener('input', updateCalculations);

    // Initial update
    updateCalculations();

    // Form submit
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const eventType = document.getElementById('event_type').value;
        const theme = document.getElementById('theme').value;
        const guestCount = parseInt(guestSlider.value);
        const budget = parseFloat(budgetInput.value);
        const venueType = document.getElementById('venue_type').value;
        const specialNotes = document.getElementById('special_notes').value;

        // UI states
        document.getElementById('placeholder-box').classList.add('hidden');
        document.getElementById('plan-output').classList.add('hidden');
        document.getElementById('loading-box').classList.remove('hidden');

        try {
            const response = await fetch('/api/party/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    event_type: eventType,
                    theme: theme,
                    guest_count: guestCount,
                    budget: budget,
                    currency: currentCurrency,
                    venue_type: venueType,
                    special_notes: specialNotes
                })
            });

            if (response.status === 401) {
                window.location.href = `/login?next=${encodeURIComponent(window.location.pathname)}`;
                return;
            }

            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || 'Failed to generate party plan');
            }

            const data = await response.json();
            currentPartyData = data.plan;
            renderPartyPlan(data.plan, budget, guestCount);
            showToast('Event Production Plan generated & saved!', 'success');

        } catch (err) {
            console.error(err);
            showToast(err.message || 'Error communicating with AI service', 'error');
            document.getElementById('placeholder-box').classList.remove('hidden');
        } finally {
            document.getElementById('loading-box').classList.add('hidden');
        }
    });

    // Tier buttons
    const tierThrifty = document.getElementById('tier-btn-thrifty');
    const tierBalanced = document.getElementById('tier-btn-balanced');
    const tierLuxe = document.getElementById('tier-btn-luxe');

    if (tierThrifty && tierBalanced && tierLuxe) {
        tierThrifty.addEventListener('click', () => switchPartyTier('thrifty'));
        tierBalanced.addEventListener('click', () => switchPartyTier('balanced'));
        tierLuxe.addEventListener('click', () => switchPartyTier('luxe'));
    }

    // Copy Summary button
    const copyBtn = document.getElementById('copy-summary-btn');
    if (copyBtn) {
        copyBtn.addEventListener('click', () => {
            if (!currentPartyData) return;
            const text = `${currentPartyData.title}\nTotal Budget: ${currentCurrency}${currentPartyData.total_allocated} (${currentCurrency}${currentPartyData.per_guest_cost}/guest)\n\nNarrative:\n${currentPartyData.summary}\n\nVibe:\n${currentPartyData.music_and_vibe?.vibe_description || ''}`;
            copyText(text, 'Party plan copied to clipboard!');
        });
    }
});

function renderPartyPlan(plan, budget, guestCount) {
    document.getElementById('plan-output').classList.remove('hidden');

    document.getElementById('plan-title').textContent = plan.title;
    document.getElementById('plan-summary').textContent = plan.summary;
    document.getElementById('plan-per-guest').textContent = `${currentCurrency}${Number(plan.per_guest_cost || (budget / guestCount)).toFixed(2)}/guest`;
    document.getElementById('plan-total-budget').textContent = `Total Budget: ${currentCurrency}${Number(budget).toLocaleString()} (${guestCount} guests)`;

    // Music & Lighting
    const vibe = plan.music_and_vibe || {};
    document.getElementById('vibe-genres').textContent = (vibe.recommended_genres || []).join(' • ') || 'Modern Nu-Disco & Upbeat Chillout';
    document.getElementById('vibe-lighting').textContent = vibe.lighting_setup || 'Warm low ambient lighting + dynamic accent washes';

    // Chart.js Donut
    const labels = (plan.budget_breakdown || []).map(b => b.category);
    const amounts = (plan.budget_breakdown || []).map(b => b.allocated_amount);
    renderBudgetChart('partyChart', labels, amounts, ['#6366f1', '#10b981', '#f59e0b', '#ec4899', '#64748b']);

    // Default tier
    switchPartyTier('balanced');

    // Timeline Rendering
    const timelineContainer = document.getElementById('timeline-container');
    timelineContainer.innerHTML = '';
    (plan.timeline || []).forEach((item, idx) => {
        const itemDiv = document.createElement('div');
        itemDiv.className = 'flex items-start gap-3 p-3 rounded-xl bg-slate-50 border border-slate-200';
        itemDiv.innerHTML = `
            <div class="px-2.5 py-1 rounded-lg bg-indigo-600 text-white font-mono font-bold text-[11px] flex-shrink-0">
                ${item.time}
            </div>
            <div>
                <h5 class="font-bold text-xs text-slate-800">${item.action}</h5>
                <p class="text-[11px] text-slate-600 mt-0.5">${item.details}</p>
            </div>
        `;
        timelineContainer.appendChild(itemDiv);
    });

    // Itemized Tables
    const tablesContainer = document.getElementById('breakdown-tables-container');
    tablesContainer.innerHTML = '';
    (plan.budget_breakdown || []).forEach(cat => {
        const catCard = document.createElement('div');
        catCard.className = 'border border-slate-200 rounded-xl overflow-hidden bg-slate-50/50';

        let itemsHtml = (cat.items || []).map(item => `
            <tr class="border-b border-slate-100 hover:bg-white text-xs">
                <td class="p-3 font-semibold text-slate-800">${item.name}</td>
                <td class="p-3 text-slate-500 hidden sm:table-cell">${item.tip || '-'}</td>
                <td class="p-3 text-center">
                    <span class="px-2 py-0.5 rounded-full text-[10px] font-bold ${
                        item.priority === 'Essential' ? 'bg-indigo-100 text-indigo-800' : 'bg-slate-200 text-slate-700'
                    }">${item.priority || 'Standard'}</span>
                </td>
                <td class="p-3 text-right font-mono font-bold text-slate-900">${currentCurrency}${Number(item.est_cost).toLocaleString()}</td>
            </tr>
        `).join('');

        catCard.innerHTML = `
            <div class="px-4 py-2.5 bg-slate-100/90 flex justify-between items-center text-xs font-bold text-slate-700 border-b border-slate-200">
                <span>${cat.category} (${cat.percentage}%)</span>
                <span class="font-mono text-indigo-700">${currentCurrency}${Number(cat.allocated_amount).toLocaleString()}</span>
            </div>
            <table class="w-full text-left">
                <thead>
                    <tr class="text-[10px] uppercase tracking-wider text-slate-400 bg-slate-50/80 border-b border-slate-200">
                        <th class="p-3">Production Element</th>
                        <th class="p-3 hidden sm:table-cell">Hosting Strategy & Tip</th>
                        <th class="p-3 text-center">Priority</th>
                        <th class="p-3 text-right">Est. Cost</th>
                    </tr>
                </thead>
                <tbody>${itemsHtml}</tbody>
            </table>
        `;
        tablesContainer.appendChild(catCard);
    });

    // Hacks
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

function switchPartyTier(tierKey) {
    if (!currentPartyData || !currentPartyData.tiers) return;
    const tier = currentPartyData.tiers[tierKey];
    if (!tier) return;

    ['thrifty', 'balanced', 'luxe'].forEach(key => {
        const btn = document.getElementById(`tier-btn-${key}`);
        if (btn) {
            if (key === tierKey) {
                btn.className = 'tier-tab-btn py-2 rounded-lg bg-white text-indigo-700 shadow-xs transition-all text-center font-bold';
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
        li.innerHTML = `<i data-lucide="arrow-right" class="w-3.5 h-3.5 text-indigo-600 flex-shrink-0 mt-0.5"></i><span>${choice}</span>`;
        choicesList.appendChild(li);
    });

    lucide.createIcons({ root: choicesList });
}
