// Ultimate Travel Agent — Local Web Interface Client Logic
let currentTrip = null;

// Tab Switching
function initTabs() {
  document.querySelectorAll(".tab-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
      document.querySelectorAll(".tab-pane").forEach((p) => p.classList.remove("active"));
      btn.classList.add("active");
      const targetId = btn.getAttribute("data-tab");
      const targetPane = document.getElementById(targetId);
      if (targetPane) targetPane.classList.add("active");
    });
  });
}

// Format Verification Level Badge
function renderVerificationBadge(level) {
  const lvl = (level || "unverified").toLowerCase();
  let badgeClass = "badge-unverified";
  if (lvl === "official_verified") badgeClass = "badge-official";
  else if (lvl === "cross_checked") badgeClass = "badge-cross_checked";
  else if (lvl === "community_recommended") badgeClass = "badge-community";
  else if (lvl === "social_discovery_only") badgeClass = "badge-social";
  else if (lvl === "outdated") badgeClass = "badge-error";
  return `<span class="badge ${badgeClass}">${lvl}</span>`;
}

// Load Example
async function loadExample(exampleKey) {
  try {
    const res = await fetch(`/api/examples/${exampleKey}`);
    if (!res.ok) throw new Error("Impossible de charger l'exemple.");
    currentTrip = await res.json();
    populateTripData(currentTrip);
  } catch (err) {
    alert(`Erreur : ${err.message}`);
  }
}

// Populate Trip Data across all UI views
async function populateTripData(trip) {
  if (!trip) return;

  // Header and title
  document.getElementById("trip-header-title").textContent = trip.title || "Voyage Sans Titre";
  document.getElementById("trip-header-subtitle").textContent = 
    `${trip.trip_type} • Du ${trip.start_date} au ${trip.end_date} • ${trip.total_days || (trip.itinerary ? trip.itinerary.length : 0)} jours`;

  // 1. Run Validation & Update Overview
  await updateValidationView(trip);

  // 2. Populate Itinerary & Activities
  updateItineraryView(trip);

  // 3. Populate Budget & Bookings
  await updateBudgetView(trip);

  // 4. Populate Inter-City Routes
  updateRoutesView(trip);

  // 5. Populate Multi-Agent Pipeline (9 steps)
  await updateMultiAgentView(trip);

  // 6. Populate Contingency & Preparation
  await updateContingencyView(trip);

  // 7. Update Markdown Export
  await updateExportView(trip);
}

// 1. Validation View
async function updateValidationView(trip) {
  const container = document.getElementById("validation-container");
  if (!container) return;

  try {
    const res = await fetch("/api/trips/validate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(trip),
    });
    const data = await res.json();

    const stats = data.summary_stats || {};
    let html = `
      <div class="grid-4" style="margin-bottom: 1.5rem;">
        <div class="stat-box">
          <div class="stat-val">${stats.days || 0}j / ${stats.nights || 0}n</div>
          <div class="stat-label">Durée</div>
        </div>
        <div class="stat-box">
          <div class="stat-val">${stats.travelers || 0}</div>
          <div class="stat-label">Voyageurs</div>
        </div>
        <div class="stat-box">
          <div class="stat-val">${stats.activities || 0}</div>
          <div class="stat-label">Activités & POIs</div>
        </div>
        <div class="stat-box">
          <div class="stat-val">${(stats.grand_total || 0).toFixed(2)} ${stats.currency || "EUR"}</div>
          <div class="stat-label">Budget Consolidé</div>
        </div>
      </div>
    `;

    if (data.valid) {
      html += `<div class="alert alert-success">✅ <strong>Cohérence validée :</strong> Aucun blocage critique détecté sur l'itinéraire, les dates ou l'intégrité référentielle.</div>`;
    } else {
      html += `<div class="alert alert-danger">❌ <strong>Erreurs de cohérence (${data.errors.length}) :</strong><ul>${data.errors.map(e => `<li>${e}</li>`).join("")}</ul></div>`;
    }

    if (data.warnings && data.warnings.length > 0) {
      html += `<div class="alert alert-warning">⚠️ <strong>Avertissements (${data.warnings.length}) :</strong><ul>${data.warnings.map(w => `<li>${w}</li>`).join("")}</ul></div>`;
    }

    html += `<div class="grid-2">
      <div class="card" style="margin-bottom: 0;">
        <div class="card-title">Données Confirmées (${data.confirmed_data ? data.confirmed_data.length : 0})</div>
        <ul>${(data.confirmed_data || []).map(c => `<li><span style="color: var(--success-text);">✔</span> ${c}</li>`).join("")}</ul>
      </div>
      <div class="card" style="margin-bottom: 0;">
        <div class="card-title">Données Non Vérifiées & Estimations (${data.unverified_data ? data.unverified_data.length : 0})</div>
        <ul>${(data.unverified_data || []).map(u => `<li><span style="color: var(--warning-text);">⚠️</span> ${u}</li>`).join("")}</ul>
      </div>
    </div>`;

    container.innerHTML = html;
  } catch (err) {
    container.innerHTML = `<div class="alert alert-danger">Erreur de validation : ${err.message}</div>`;
  }
}

// 2. Itinerary View
function updateItineraryView(trip) {
  const container = document.getElementById("itinerary-container");
  if (!container) return;

  let html = "";
  if (trip.stages && trip.stages.length > 0) {
    html += `<div class="card">
      <div class="card-title">Étapes du Voyage (${trip.stages.length})</div>
      <table>
        <thead><tr><th>Étape</th><th>Dates</th><th>Nuits</th><th>Niveau de preuve</th><th>Notes</th></tr></thead>
        <tbody>
          ${trip.stages.map(s => `
            <tr>
              <td><strong>${s.title || s.id}</strong></td>
              <td>${s.arrival_date || "?"} ➔ ${s.departure_date || "?"}</td>
              <td>${s.nights}</td>
              <td>${renderVerificationBadge(s.verification_level)}</td>
              <td>${s.notes || "-"}</td>
            </tr>
          `).join("")}
        </tbody>
      </table>
    </div>`;
  }

  html += `<div class="card"><div class="card-title">Planning Chronologique Jour par Jour</div>`;
  if (trip.itinerary && trip.itinerary.length > 0) {
    trip.itinerary.forEach((day) => {
      html += `
        <div class="day-card">
          <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
            <h3 style="color: #fff;">Jour ${day.day_number} ${day.date ? `(${day.date})` : ""} — ${day.theme || ""}</h3>
          </div>
          ${day.weather_contingency_notes ? `<div style="font-size: 0.85rem; color: #93c5fd; margin-bottom: 0.75rem;">☔ <em>Repli météo : ${day.weather_contingency_notes}</em></div>` : ""}
          <div class="timeline">
            ${day.items.map(item => `
              <div class="timeline-item">
                <div class="timeline-time">${item.time}</div>
                <div style="flex: 1;">
                  <strong>${item.title}</strong> <span class="badge badge-community">${item.item_type}</span>
                  <span style="color: var(--text-muted); font-size: 0.8rem; margin-left: 0.5rem;">${item.duration_minutes} min</span>
                  ${item.notes ? `<div style="font-size: 0.85rem; color: var(--text-muted);">${item.notes}</div>` : ""}
                </div>
              </div>
            `).join("")}
          </div>
        </div>
      `;
    });
  } else {
    html += `<p style="color: var(--text-muted);">Aucune journée détaillée n'est enregistrée.</p>`;
  }
  html += `</div>`;

  // Detailed Activities with V1.1 Enriched fields
  if (trip.activities && trip.activities.length > 0) {
    html += `<div class="card"><div class="card-title">Activités Curationnées & Fiches Détaillées (${trip.activities.length})</div><div class="grid-2">`;
    trip.activities.forEach(act => {
      const bookingLink = act.official_booking_url ? `<a href="${act.official_booking_url}" target="_blank" class="btn btn-sm btn-secondary" style="margin-top: 0.5rem;">Billetterie Officielle ↗</a>` : "";
      html += `
        <div class="stat-box" style="text-align: left; padding: 1.25rem;">
          <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 0.5rem; margin-bottom: 0.5rem;">
            <h4 style="color: #fff; font-size: 1.05rem;">${act.title}</h4>
            ${renderVerificationBadge(act.verification_level)}
          </div>
          <div style="font-size: 0.85rem; color: var(--secondary); margin-bottom: 0.5rem;">
            ${act.neighborhood || ''} • Catégorie : <strong>${act.category}</strong> • ${act.duration_minutes} min • ${act.estimated_cost} ${act.currency}
          </div>
          <p style="font-size: 0.9rem; margin-bottom: 0.75rem;">${act.description}</p>
          ${act.anecdote ? `<div style="font-size: 0.85rem; color: #cbd5e1; background: var(--bg-card); padding: 0.5rem; border-radius: var(--radius); margin-bottom: 0.5rem;">💡 <em>${act.anecdote}</em></div>` : ""}
          <div style="font-size: 0.8rem; color: var(--text-muted);">
            ${act.best_time_slot ? `<div>🕒 <strong>Créneau optimal :</strong> ${act.best_time_slot}</div>` : ""}
            ${act.quiet_slot_advice ? `<div>👥 <strong>Stratégie foule :</strong> ${act.quiet_slot_advice}</div>` : ""}
            ${act.weather_alternative ? `<div>☔ <strong>Plan B météo :</strong> ${act.weather_alternative}</div>` : ""}
            ${act.closure_alternative ? `<div>🚪 <strong>Si fermé :</strong> ${act.closure_alternative}</div>` : ""}
          </div>
          ${bookingLink}
        </div>
      `;
    });
    html += `</div></div>`;
  }

  container.innerHTML = html;
}

// 3. Budget View
async function updateBudgetView(trip) {
  const container = document.getElementById("budget-container");
  if (!container) return;

  try {
    const res = await fetch("/api/trips/budget", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ trip, safety_buffer_pct: 12.0 }),
    });
    const budget = await res.json();

    let html = `
      <div class="grid-3" style="margin-bottom: 1.5rem;">
        <div class="stat-box">
          <div class="stat-val">${budget.total_estimated_cost.toFixed(2)} ${budget.currency}</div>
          <div class="stat-label">Dépenses Directes</div>
        </div>
        <div class="stat-box">
          <div class="stat-val">+${budget.safety_buffer_amount.toFixed(2)} ${budget.currency}</div>
          <div class="stat-label">Réserve Sécurité (${budget.safety_buffer_percentage}%)</div>
        </div>
        <div class="stat-box">
          <div class="stat-val" style="color: var(--success-text);">${budget.grand_total.toFixed(2)} ${budget.currency}</div>
          <div class="stat-label">TOTAL GÉNÉRAL CONSOLIDÉ</div>
        </div>
      </div>

      <div class="card">
        <div class="card-title">Ventilation par Poste de Dépense</div>
        <table>
          <thead><tr><th>Poste</th><th>Montant</th><th>Part</th><th>Niveau de Preuve</th></tr></thead>
          <tbody>
            ${Object.entries(budget.categories || {}).map(([cat, val]) => {
              const pct = ((val.amount / budget.total_estimated_cost) * 100).toFixed(1);
              return `
                <tr>
                  <td><strong>${cat.toUpperCase()}</strong></td>
                  <td>${val.amount.toFixed(2)} ${val.currency}</td>
                  <td>${pct}%</td>
                  <td>${renderVerificationBadge(val.verification_level)}</td>
                </tr>
              `;
            }).join("")}
          </tbody>
        </table>
      </div>
    `;

    if (trip.reservations && trip.reservations.length > 0) {
      html += `
        <div class="card">
          <div class="card-title">Réservations & Démarches Manuelles Requises (${trip.reservations.length})</div>
          <div style="font-size: 0.85rem; color: var(--text-muted); margin-bottom: 1rem;">
            🔒 <em>Principe de sécurité : Ultimate Travel Agent n'effectue aucun paiement ni réservation automatique.</em>
          </div>
          <table>
            <thead><tr><th>Titre</th><th>Obligatoire</th><th>Coût estimé</th><th>Action à Réaliser</th><th>Lien Officiel</th></tr></thead>
            <tbody>
              ${trip.reservations.map(r => `
                <tr>
                  <td><strong>${r.title}</strong></td>
                  <td>${r.mandatory ? '<span style="color: var(--danger-text);">OUI</span>' : 'Optionnel'}</td>
                  <td>${r.estimated_cost ? `${r.estimated_cost.toFixed(2)} ${r.currency}` : 'Inclus'}</td>
                  <td>${r.action_required || 'Réservation manuelle requise'}</td>
                  <td>${r.official_booking_url ? `<a href="${r.official_booking_url}" target="_blank" class="btn btn-sm btn-secondary">Portail Officiel ↗</a>` : '-'}</td>
                </tr>
              `).join("")}
            </tbody>
          </table>
        </div>
      `;
    }

    container.innerHTML = html;
  } catch (err) {
    container.innerHTML = `<div class="alert alert-danger">Erreur budget : ${err.message}</div>`;
  }
}

// 4. Inter-City Routes View
function updateRoutesView(trip) {
  const container = document.getElementById("routes-container");
  if (!container) return;

  if (!trip.inter_city_routes || trip.inter_city_routes.length === 0) {
    container.innerHTML = `
      <div class="card">
        <div class="card-title">Comparateur d'Itinéraires Inter-Villes</div>
        <p style="color: var(--text-muted);">Ce voyage ne contient pas encore d'options concurrentes modélisées. Le moteur de recommandation multi-critères s'active lorsqu'une liaison inter-villes est configurée.</p>
      </div>
    `;
    return;
  }

  let html = "";
  trip.inter_city_routes.forEach((route) => {
    html += `
      <div class="card">
        <div class="card-title">
          <span>Trajet : ${route.origin} ➔ ${route.destination}</span>
          <span class="badge badge-official">${route.options ? route.options.length : 0} options comparées</span>
        </div>
        <table>
          <thead>
            <tr><th>Option</th><th>Mode</th><th>Durée</th><th>Correspondances</th><th>Coût estimé</th><th>Confort</th><th>Bilan CO2</th><th>Lien officiel</th></tr>
          </thead>
          <tbody>
            ${(route.options || []).map(opt => `
              <tr>
                <td><strong>${opt.id}</strong></td>
                <td><span class="badge badge-community">${opt.mode}</span></td>
                <td>${opt.estimated_duration_minutes} min</td>
                <td>${opt.transfers_count} correspondance(s)</td>
                <td>${opt.estimated_cost.toFixed(2)} ${opt.currency}</td>
                <td>${"★".repeat(opt.comfort_level)}${"☆".repeat(5 - opt.comfort_level)}</td>
                <td>${opt.carbon_footprint_kg ? `${opt.carbon_footprint_kg} kg` : 'Éco'}</td>
                <td>${opt.official_booking_url ? `<a href="${opt.official_booking_url}" target="_blank" class="btn btn-sm btn-secondary">Portail ↗</a>` : '-'}</td>
              </tr>
            `).join("")}
          </tbody>
        </table>
        ${route.recommendation_reason ? `
          <div class="alert alert-info" style="margin-top: 1rem;">
            💡 <strong>Recommandation du système :</strong> ${route.recommendation_reason}
          </div>
        ` : ""}
      </div>
    `;
  });

  container.innerHTML = html;
}

// 5. Multi-Agent Pipeline View (9 Steps)
async function updateMultiAgentView(trip) {
  const container = document.getElementById("multiagent-container");
  if (!container) return;

  try {
    const res = await fetch("/api/trips/plan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(trip),
    });
    const plan = await res.json();

    let html = `
      <div class="alert alert-warning" style="margin-bottom: 1.5rem;">
        🔒 <strong>Transparence Algorithmique — Mode Hors-Ligne Déterministe :</strong><br>
        <code>${plan.offline_banner.message}</code>
      </div>
      <div class="card">
        <div class="card-title">Les 9 Étapes du Pipeline Multi-Agents</div>
    `;

    (plan.stages || []).forEach(st => {
      const icon = st.status === "complete" ? "✅" : (st.status === "partial" ? "⚠️" : "❌");
      html += `
        <div class="stage-step">
          <div class="stage-header">
            <div>
              <strong style="font-size: 1.05rem; color: #fff;">${icon} Étape ${st.step_number} : ${st.name}</strong>
              <span style="font-size: 0.8rem; color: var(--text-muted); margin-left: 0.5rem;">(Agent : <code>${st.agent}</code>)</span>
            </div>
            ${renderVerificationBadge(st.verification_level)}
          </div>
          <p style="font-size: 0.95rem; margin-bottom: 0.5rem;">${st.summary}</p>
          
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; font-size: 0.82rem; margin-top: 0.5rem;">
            <div style="background: rgba(255, 255, 255, 0.02); padding: 0.5rem; border-radius: var(--radius);">
              <span style="color: var(--secondary); font-weight: 700;">Hypothèses :</span>
              <ul style="padding-left: 1.2rem;">${(st.assumptions || []).map(a => `<li>${a}</li>`).join("")}</ul>
            </div>
            <div style="background: rgba(255, 255, 255, 0.02); padding: 0.5rem; border-radius: var(--radius);">
              <span style="color: var(--warning-text); font-weight: 700;">Informations manquantes / Risques :</span>
              <ul style="padding-left: 1.2rem;">
                ${(st.missing_information || []).map(m => `<li>${m}</li>`).join("")}
                ${(st.risks || []).map(r => `<li style="color: var(--danger-text);">${r}</li>`).join("")}
              </ul>
            </div>
          </div>
        </div>
      `;
    });

    html += `</div>`;
    container.innerHTML = html;
  } catch (err) {
    container.innerHTML = `<div class="alert alert-danger">Erreur pipeline multi-agent : ${err.message}</div>`;
  }
}

// 6. Contingency View
async function updateContingencyView(trip) {
  const container = document.getElementById("contingency-container");
  if (!container) return;

  try {
    const res = await fetch("/api/trips/contingency", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(trip),
    });
    const c = await res.json();

    let html = `
      <div class="card">
        <div class="card-title">Checklist Avant Départ</div>
        <table>
          <thead><tr><th>Action / Tâche</th><th>Délai</th><th>Obligatoire</th><th>Vérification</th></tr></thead>
          <tbody>
            ${(c.pre_departure_checklist || []).map(item => `
              <tr>
                <td><strong>${item.title}</strong><div style="font-size: 0.85rem; color: var(--text-muted);">${item.action}</div></td>
                <td><code>${item.deadline}</code></td>
                <td>${item.mandatory ? '<span style="color: var(--danger-text); font-weight: 700;">OUI</span>' : 'Conseillé'}</td>
                <td><span class="badge badge-unverified">${item.verification_note}</span></td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      </div>

      <div class="card">
        <div class="card-title">Documents Administratifs & Sanitaires à Vérifier</div>
        <table>
          <thead><tr><th>Document</th><th>Condition Requise</th><th>Règle / Consigne</th><th>Statut</th></tr></thead>
          <tbody>
            ${(c.document_verification_list || []).map(doc => `
              <tr>
                <td><strong>${doc.document}</strong></td>
                <td>${doc.requirement}</td>
                <td>${doc.rule}</td>
                <td><span class="badge badge-unverified">${doc.status}</span></td>
              </tr>
            `).join("")}
          </tbody>
        </table>
      </div>

      <div class="grid-2">
        <div class="card">
          <div class="card-title">☔ Plan B Météo (Intempéries)</div>
          ${(c.weather_contingency_plan || []).map(w => `
            <div style="margin-bottom: 0.75rem; border-bottom: 1px solid var(--border); padding-bottom: 0.5rem;">
              <strong>Jour ${w.day_number} (${w.theme}) :</strong>
              <div style="font-size: 0.85rem; color: #93c5fd;">${w.general_contingency_notes}</div>
              ${(w.outdoor_contingencies || []).map(o => `
                <div style="font-size: 0.8rem; margin-top: 0.25rem;">• Repli pour <em>${o.activity}</em> : ${o.backup}</div>
              `).join("")}
            </div>
          `).join("")}
        </div>

        <div class="card">
          <div class="card-title">🚪 Plan B Fermeture d'Activité</div>
          ${(c.activity_closure_plan || []).map(cl => `
            <div style="margin-bottom: 0.75rem; border-bottom: 1px solid var(--border); padding-bottom: 0.5rem;">
              <strong>${cl.activity_title}</strong>
              <div style="font-size: 0.85rem; color: var(--text-muted);">${cl.recommended_alternative}</div>
            </div>
          `).join("")}
        </div>
      </div>

      <div class="card">
        <div class="card-title">🚨 Fiche d'Urgence Générique</div>
        <div class="alert alert-info">
          🛡️ <em>${c.generic_emergency_summary.zero_fabrication_guarantee}</em>
        </div>
        <div style="font-size: 0.9rem; display: flex; flex-direction: column; gap: 0.5rem;">
          <div>📞 <strong>Numéro d'appel d'urgence :</strong> ${c.generic_emergency_summary.emergency_dispatch_reminder}</div>
          <div>🏛️ <strong>Assistance Consulaire :</strong> ${c.generic_emergency_summary.consular_support_reminder}</div>
          <div>🏥 <strong>Assistance Médicale :</strong> ${c.generic_emergency_summary.medical_assistance_reminder}</div>
          <div>💳 <strong>Opposition Bancaire :</strong> ${c.generic_emergency_summary.lost_payment_cards_hotline}</div>
        </div>
      </div>
    `;

    container.innerHTML = html;
  } catch (err) {
    container.innerHTML = `<div class="alert alert-danger">Erreur contingency : ${err.message}</div>`;
  }
}

// 7. Markdown Export View
async function updateExportView(trip) {
  const container = document.getElementById("export-markdown-content");
  if (!container) return;

  try {
    const res = await fetch("/api/trips/export", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(trip),
    });
    const mdText = await res.text();
    container.value = mdText;
  } catch (err) {
    container.value = `Erreur lors de l'export Markdown : ${err.message}`;
  }
}

// Copy Markdown to Clipboard
function copyMarkdown() {
  const area = document.getElementById("export-markdown-content");
  if (area) {
    navigator.clipboard.writeText(area.value);
    alert("Dossier Markdown copié dans le presse-papier !");
  }
}

// Form Submission for New Trip Creation
function initForm() {
  const form = document.getElementById("trip-create-form");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const destination = document.getElementById("form-destination").value;
    const country = document.getElementById("form-country").value;
    const start_date = document.getElementById("form-start-date").value;
    const end_date = document.getElementById("form-end-date").value;
    const travelers_count = parseInt(document.getElementById("form-travelers").value, 10);
    const traveler_profile = document.getElementById("form-profile").value;
    const budget_cap = parseFloat(document.getElementById("form-budget").value) || 1000.0;
    const currency = document.getElementById("form-currency").value;
    const accommodation_style = document.getElementById("form-lodging").value;
    const pacing = document.getElementById("form-pacing").value;
    const crowd_preference = document.getElementById("form-crowd").value;
    const constraints = document.getElementById("form-constraints").value;

    const payload = {
      destination,
      country,
      start_date,
      end_date,
      travelers_count,
      traveler_profile,
      budget_cap,
      currency,
      accommodation_style,
      pacing,
      crowd_preference,
      constraints,
      interests: ["culture", "gastronomy", "patrimoine"],
    };

    try {
      const res = await fetch("/api/trips/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error("Échec de la génération du dossier");
      currentTrip = await res.json();
      populateTripData(currentTrip);
      // Switch to validation tab
      document.querySelector('[data-tab="tab-overview"]').click();
    } catch (err) {
      alert(`Erreur : ${err.message}`);
    }
  });
}

// Initialization on DOMContentLoaded
document.addEventListener("DOMContentLoaded", () => {
  initTabs();
  initForm();
  // Auto-load reference city trip so user immediately sees a live dossier
  loadExample("city-trip");
});
