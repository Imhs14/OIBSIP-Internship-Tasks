import { useState, useEffect, useRef } from "react";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, ReferenceLine } from "recharts";

const STORAGE_KEY = "bmi_app_data";

const BMI_ZONES = [
  { label: "Underweight", min: 0, max: 18.5, color: "#378ADD", bg: "#E6F1FB", text: "#0C447C" },
  { label: "Normal", min: 18.5, max: 25, color: "#639922", bg: "#EAF3DE", text: "#27500A" },
  { label: "Overweight", min: 25, max: 30, color: "#BA7517", bg: "#FAEEDA", text: "#633806" },
  { label: "Obese", min: 30, max: 100, color: "#E24B4A", bg: "#FCEBEB", text: "#791F1F" },
];

function getBMIZone(bmi) {
  return BMI_ZONES.find((z) => bmi >= z.min && bmi < z.max) || BMI_ZONES[3];
}

function calcBMI(weight, height, unit) {
  if (!weight || !height || height === 0) return null;
  if (unit === "metric") return weight / (height / 100) ** 2;
  const heightM = (Math.floor(height / 12) * 0.3048) + ((height % 12) * 0.0254);
  return (weight * 0.453592) / heightM ** 2;
}

const defaultUsers = {};

export default function BMICalculator() {
  const [data, setData] = useState(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY);
      return saved ? JSON.parse(saved) : defaultUsers;
    } catch { return defaultUsers; }
  });

  const [currentUser, setCurrentUser] = useState("");
  const [view, setView] = useState("calculator"); // calculator | history | trends | users
  const [unit, setUnit] = useState("metric");
  const [weight, setWeight] = useState("");
  const [heightCm, setHeightCm] = useState("");
  const [heightFt, setHeightFt] = useState("");
  const [heightIn, setHeightIn] = useState("");
  const [note, setNote] = useState("");
  const [newUserName, setNewUserName] = useState("");
  const [bmiResult, setBmiResult] = useState(null);
  const [saved, setSaved] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState(null);

  useEffect(() => {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(data)); }
    catch {}
  }, [data]);

  const users = Object.keys(data);
  const userRecords = currentUser ? (data[currentUser] || []) : [];

  function addUser() {
    const name = newUserName.trim();
    if (!name || data[name]) return;
    setData(d => ({ ...d, [name]: [] }));
    setCurrentUser(name);
    setNewUserName("");
    setView("calculator");
  }

  function deleteUser(name) {
    setData(d => { const nd = { ...d }; delete nd[name]; return nd; });
    if (currentUser === name) setCurrentUser("");
    setDeleteConfirm(null);
  }

  function calculate() {
    const h = unit === "metric" ? parseFloat(heightCm) : parseFloat(heightFt) * 12 + parseFloat(heightIn || 0);
    const w = parseFloat(weight);
    const bmi = calcBMI(w, h, unit);
    if (bmi && bmi > 0 && bmi < 100) setBmiResult(parseFloat(bmi.toFixed(1)));
    else setBmiResult(null);
    setSaved(false);
  }

  function saveEntry() {
    if (!currentUser || !bmiResult) return;
    const h = unit === "metric"
      ? `${heightCm} cm`
      : `${heightFt}'${heightIn || 0}"`;
    const entry = {
      id: Date.now(),
      date: new Date().toISOString(),
      bmi: bmiResult,
      weight: `${weight} ${unit === "metric" ? "kg" : "lbs"}`,
      height: h,
      note: note.trim(),
    };
    setData(d => ({ ...d, [currentUser]: [entry, ...(d[currentUser] || [])] }));
    setSaved(true);
    setNote("");
  }

  function deleteEntry(userId, entryId) {
    setData(d => ({ ...d, [userId]: d[userId].filter(e => e.id !== entryId) }));
  }

  const zone = bmiResult ? getBMIZone(bmiResult) : null;

  const chartData = [...userRecords].reverse().map(r => ({
    date: new Date(r.date).toLocaleDateString("en-IN", { day: "numeric", month: "short" }),
    bmi: r.bmi,
  }));

  const avgBMI = userRecords.length
    ? (userRecords.reduce((s, r) => s + r.bmi, 0) / userRecords.length).toFixed(1)
    : null;

  const trend = userRecords.length >= 2
    ? (userRecords[0].bmi - userRecords[userRecords.length - 1].bmi).toFixed(1)
    : null;

  return (
    <div style={{ fontFamily: "var(--font-sans)", maxWidth: 720, margin: "0 auto", padding: "1.5rem 1rem" }}>
      <h2 style={{ sr: "BMI Tracker", fontSize: 22, fontWeight: 500, margin: "0 0 4px", color: "var(--color-text-primary)" }}>
        BMI Tracker
      </h2>
      <p style={{ fontSize: 14, color: "var(--color-text-secondary)", margin: "0 0 1.5rem" }}>
        Track body mass index for multiple users over time
      </p>

      {/* User selector */}
      <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginBottom: "1.25rem", alignItems: "center" }}>
        {users.map(u => (
          <button
            key={u}
            onClick={() => { setCurrentUser(u); setView("calculator"); setBmiResult(null); setSaved(false); }}
            style={{
              padding: "6px 14px", borderRadius: "var(--border-radius-md)",
              border: currentUser === u ? "1.5px solid #639922" : "0.5px solid var(--color-border-tertiary)",
              background: currentUser === u ? "#EAF3DE" : "var(--color-background-secondary)",
              color: currentUser === u ? "#27500A" : "var(--color-text-primary)",
              fontSize: 13, fontWeight: currentUser === u ? 500 : 400, cursor: "pointer",
            }}
          >{u}</button>
        ))}
        <button
          onClick={() => setView("users")}
          style={{ padding: "6px 12px", borderRadius: "var(--border-radius-md)", border: "0.5px dashed var(--color-border-secondary)", background: "transparent", color: "var(--color-text-secondary)", fontSize: 13, cursor: "pointer" }}
        >+ Add user</button>
      </div>

      {/* Nav tabs */}
      {currentUser && (
        <div style={{ display: "flex", gap: 2, borderBottom: "0.5px solid var(--color-border-tertiary)", marginBottom: "1.5rem" }}>
          {["calculator", "history", "trends"].map(v => (
            <button
              key={v}
              onClick={() => setView(v)}
              style={{
                padding: "8px 16px", background: "transparent", cursor: "pointer", fontSize: 13,
                border: "none", borderBottom: view === v ? "2px solid #639922" : "2px solid transparent",
                color: view === v ? "#27500A" : "var(--color-text-secondary)",
                fontWeight: view === v ? 500 : 400,
                textTransform: "capitalize",
              }}
            >{v}</button>
          ))}
        </div>
      )}

      {/* Add user panel */}
      {view === "users" && (
        <div style={{ background: "var(--color-background-primary)", border: "0.5px solid var(--color-border-tertiary)", borderRadius: "var(--border-radius-lg)", padding: "1.25rem" }}>
          <p style={{ margin: "0 0 1rem", fontWeight: 500, color: "var(--color-text-primary)" }}>Manage users</p>
          <div style={{ display: "flex", gap: 8, marginBottom: "1.25rem" }}>
            <input
              value={newUserName} onChange={e => setNewUserName(e.target.value)}
              onKeyDown={e => e.key === "Enter" && addUser()}
              placeholder="Enter name…" style={{ flex: 1 }}
            />
            <button onClick={addUser} style={{ padding: "0 16px" }}>Add</button>
          </div>
          {users.length === 0 && <p style={{ color: "var(--color-text-secondary)", fontSize: 13 }}>No users yet.</p>}
          {users.map(u => (
            <div key={u} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "10px 0", borderTop: "0.5px solid var(--color-border-tertiary)" }}>
              <div>
                <span style={{ fontWeight: 500, fontSize: 14 }}>{u}</span>
                <span style={{ fontSize: 12, color: "var(--color-text-secondary)", marginLeft: 8 }}>{(data[u] || []).length} entries</span>
              </div>
              {deleteConfirm === u ? (
                <div style={{ display: "flex", gap: 6 }}>
                  <button onClick={() => deleteUser(u)} style={{ fontSize: 12, color: "#E24B4A", border: "0.5px solid #E24B4A", background: "transparent", padding: "4px 10px", borderRadius: "var(--border-radius-md)", cursor: "pointer" }}>Confirm</button>
                  <button onClick={() => setDeleteConfirm(null)} style={{ fontSize: 12, padding: "4px 10px", cursor: "pointer" }}>Cancel</button>
                </div>
              ) : (
                <button onClick={() => setDeleteConfirm(u)} style={{ fontSize: 12, color: "var(--color-text-secondary)", background: "transparent", border: "none", cursor: "pointer" }}>Remove</button>
              )}
            </div>
          ))}
        </div>
      )}

      {/* No user selected */}
      {!currentUser && view !== "users" && (
        <div style={{ textAlign: "center", padding: "3rem 1rem", color: "var(--color-text-secondary)", fontSize: 14 }}>
          Select or add a user to get started.
        </div>
      )}

      {/* Calculator */}
      {currentUser && view === "calculator" && (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
          <div style={{ background: "var(--color-background-primary)", border: "0.5px solid var(--color-border-tertiary)", borderRadius: "var(--border-radius-lg)", padding: "1.25rem", gridColumn: "span 2" }}>
            <div style={{ display: "flex", gap: 8, marginBottom: "1.25rem" }}>
              {["metric", "imperial"].map(u => (
                <button key={u} onClick={() => { setUnit(u); setBmiResult(null); setSaved(false); }}
                  style={{
                    padding: "6px 16px", borderRadius: "var(--border-radius-md)", cursor: "pointer",
                    border: unit === u ? "1.5px solid #378ADD" : "0.5px solid var(--color-border-tertiary)",
                    background: unit === u ? "#E6F1FB" : "var(--color-background-secondary)",
                    color: unit === u ? "#0C447C" : "var(--color-text-secondary)", fontSize: 13,
                    textTransform: "capitalize",
                  }}
                >{u}</button>
              ))}
            </div>

            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem", marginBottom: "1rem" }}>
              <div>
                <label style={{ fontSize: 12, color: "var(--color-text-secondary)", display: "block", marginBottom: 6 }}>
                  Weight ({unit === "metric" ? "kg" : "lbs"})
                </label>
                <input type="number" value={weight} onChange={e => setWeight(e.target.value)} placeholder={unit === "metric" ? "e.g. 70" : "e.g. 154"} />
              </div>
              {unit === "metric" ? (
                <div>
                  <label style={{ fontSize: 12, color: "var(--color-text-secondary)", display: "block", marginBottom: 6 }}>Height (cm)</label>
                  <input type="number" value={heightCm} onChange={e => setHeightCm(e.target.value)} placeholder="e.g. 170" />
                </div>
              ) : (
                <div>
                  <label style={{ fontSize: 12, color: "var(--color-text-secondary)", display: "block", marginBottom: 6 }}>Height (ft / in)</label>
                  <div style={{ display: "flex", gap: 6 }}>
                    <input type="number" value={heightFt} onChange={e => setHeightFt(e.target.value)} placeholder="ft" style={{ width: "50%" }} />
                    <input type="number" value={heightIn} onChange={e => setHeightIn(e.target.value)} placeholder="in" style={{ width: "50%" }} />
                  </div>
                </div>
              )}
            </div>

            <button onClick={calculate} style={{ width: "100%", padding: "10px", fontWeight: 500, marginBottom: "1rem", background: "#EAF3DE", color: "#27500A", border: "0.5px solid #639922", borderRadius: "var(--border-radius-md)", cursor: "pointer", fontSize: 14 }}>
              Calculate BMI
            </button>

            {bmiResult && zone && (
              <div style={{ background: zone.bg, border: `0.5px solid ${zone.color}`, borderRadius: "var(--border-radius-md)", padding: "1rem", marginBottom: "1rem" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                  <div>
                    <div style={{ fontSize: 36, fontWeight: 500, color: zone.text, lineHeight: 1 }}>{bmiResult}</div>
                    <div style={{ fontSize: 13, color: zone.text, marginTop: 4 }}>{zone.label}</div>
                  </div>
                  <div style={{ fontSize: 12, color: zone.text, textAlign: "right" }}>
                    <div>Normal: 18.5 – 24.9</div>
                    <div style={{ marginTop: 2 }}>Your range: {zone.min}–{zone.max < 100 ? zone.max : "+"}</div>
                  </div>
                </div>
                {/* BMI bar */}
                <div style={{ marginTop: "0.75rem", position: "relative" }}>
                  <div style={{ display: "flex", borderRadius: 4, overflow: "hidden", height: 8, background: "rgba(0,0,0,0.1)" }}>
                    {BMI_ZONES.map(z => (
                      <div key={z.label} style={{ flex: z.label === "Obese" ? 1 : (z.max - z.min), background: z.color, opacity: 0.6 }} />
                    ))}
                  </div>
                  {/* Marker */}
                  <div style={{
                    position: "absolute", top: -4, width: 16, height: 16, borderRadius: "50%", border: "2px solid white",
                    background: zone.color, transform: "translateX(-50%)",
                    left: `${Math.min(Math.max(((bmiResult - 10) / 30) * 100, 2), 98)}%`,
                    transition: "left 0.4s ease",
                  }} />
                </div>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: 10, color: zone.text, marginTop: 12, opacity: 0.8 }}>
                  {BMI_ZONES.map(z => <span key={z.label}>{z.label}</span>)}
                </div>
              </div>
            )}

            {bmiResult && currentUser && (
              <div>
                <input
                  value={note} onChange={e => setNote(e.target.value)}
                  placeholder="Add a note (optional)…"
                  style={{ width: "100%", marginBottom: 8, boxSizing: "border-box" }}
                />
                <button
                  onClick={saveEntry}
                  disabled={saved}
                  style={{ width: "100%", padding: "9px", cursor: saved ? "default" : "pointer", opacity: saved ? 0.6 : 1, fontSize: 13, borderRadius: "var(--border-radius-md)", border: "0.5px solid var(--color-border-secondary)", background: "var(--color-background-secondary)", color: "var(--color-text-primary)" }}
                >
                  {saved ? "✓ Saved to history" : `Save for ${currentUser}`}
                </button>
              </div>
            )}
          </div>

          {/* BMI reference card */}
          <div style={{ background: "var(--color-background-secondary)", borderRadius: "var(--border-radius-lg)", padding: "1rem", gridColumn: "span 2", display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 8 }}>
            {BMI_ZONES.map(z => (
              <div key={z.label} style={{ background: z.bg, borderRadius: "var(--border-radius-md)", padding: "8px 10px", border: `0.5px solid ${z.color}` }}>
                <div style={{ fontSize: 11, color: z.text, fontWeight: 500 }}>{z.label}</div>
                <div style={{ fontSize: 12, color: z.text, opacity: 0.8 }}>{z.min}–{z.max < 100 ? z.max : "40+"}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* History */}
      {currentUser && view === "history" && (
        <div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 10, marginBottom: "1.5rem" }}>
            <div style={{ background: "var(--color-background-secondary)", borderRadius: "var(--border-radius-md)", padding: "12px 14px" }}>
              <div style={{ fontSize: 12, color: "var(--color-text-secondary)", marginBottom: 4 }}>Entries</div>
              <div style={{ fontSize: 24, fontWeight: 500 }}>{userRecords.length}</div>
            </div>
            <div style={{ background: "var(--color-background-secondary)", borderRadius: "var(--border-radius-md)", padding: "12px 14px" }}>
              <div style={{ fontSize: 12, color: "var(--color-text-secondary)", marginBottom: 4 }}>Avg BMI</div>
              <div style={{ fontSize: 24, fontWeight: 500 }}>{avgBMI || "–"}</div>
            </div>
            <div style={{ background: "var(--color-background-secondary)", borderRadius: "var(--border-radius-md)", padding: "12px 14px" }}>
              <div style={{ fontSize: 12, color: "var(--color-text-secondary)", marginBottom: 4 }}>Trend</div>
              <div style={{ fontSize: 24, fontWeight: 500, color: trend === null ? undefined : parseFloat(trend) <= 0 ? "#639922" : "#E24B4A" }}>
                {trend !== null ? (parseFloat(trend) > 0 ? `+${trend}` : trend) : "–"}
              </div>
            </div>
          </div>

          {userRecords.length === 0 ? (
            <p style={{ color: "var(--color-text-secondary)", fontSize: 14, textAlign: "center", padding: "2rem" }}>No entries yet. Calculate and save your first BMI.</p>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {userRecords.map(r => {
                const z = getBMIZone(r.bmi);
                return (
                  <div key={r.id} style={{ background: "var(--color-background-primary)", border: "0.5px solid var(--color-border-tertiary)", borderRadius: "var(--border-radius-md)", padding: "12px 14px", display: "flex", alignItems: "center", gap: 12 }}>
                    <div style={{ width: 48, height: 48, borderRadius: "var(--border-radius-md)", background: z.bg, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                      <span style={{ fontSize: 15, fontWeight: 500, color: z.text }}>{r.bmi}</span>
                    </div>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontSize: 13, fontWeight: 500, color: "var(--color-text-primary)" }}>
                        {z.label} <span style={{ fontSize: 11, fontWeight: 400, color: z.text, background: z.bg, padding: "2px 7px", borderRadius: 4, marginLeft: 4 }}>{r.weight} · {r.height}</span>
                      </div>
                      {r.note && <div style={{ fontSize: 12, color: "var(--color-text-secondary)", marginTop: 2, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{r.note}</div>}
                      <div style={{ fontSize: 11, color: "var(--color-text-secondary)", marginTop: 2 }}>
                        {new Date(r.date).toLocaleString("en-IN", { dateStyle: "medium", timeStyle: "short" })}
                      </div>
                    </div>
                    <button onClick={() => deleteEntry(currentUser, r.id)}
                      style={{ background: "transparent", border: "none", cursor: "pointer", color: "var(--color-text-secondary)", fontSize: 12, padding: "4px 8px", borderRadius: "var(--border-radius-md)" }}
                      aria-label="Delete entry">×</button>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      )}

      {/* Trends */}
      {currentUser && view === "trends" && (
        <div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 10, marginBottom: "1.5rem" }}>
            <div style={{ background: "var(--color-background-secondary)", borderRadius: "var(--border-radius-md)", padding: "12px 14px" }}>
              <div style={{ fontSize: 12, color: "var(--color-text-secondary)", marginBottom: 4 }}>Current BMI</div>
              <div style={{ fontSize: 24, fontWeight: 500 }}>{userRecords[0]?.bmi ?? "–"}</div>
            </div>
            <div style={{ background: "var(--color-background-secondary)", borderRadius: "var(--border-radius-md)", padding: "12px 14px" }}>
              <div style={{ fontSize: 12, color: "var(--color-text-secondary)", marginBottom: 4 }}>Min BMI</div>
              <div style={{ fontSize: 24, fontWeight: 500 }}>
                {userRecords.length ? Math.min(...userRecords.map(r => r.bmi)).toFixed(1) : "–"}
              </div>
            </div>
            <div style={{ background: "var(--color-background-secondary)", borderRadius: "var(--border-radius-md)", padding: "12px 14px" }}>
              <div style={{ fontSize: 12, color: "var(--color-text-secondary)", marginBottom: 4 }}>Max BMI</div>
              <div style={{ fontSize: 24, fontWeight: 500 }}>
                {userRecords.length ? Math.max(...userRecords.map(r => r.bmi)).toFixed(1) : "–"}
              </div>
            </div>
          </div>

          {chartData.length < 2 ? (
            <div style={{ background: "var(--color-background-secondary)", borderRadius: "var(--border-radius-lg)", padding: "2rem", textAlign: "center" }}>
              <p style={{ color: "var(--color-text-secondary)", fontSize: 14 }}>Add at least 2 entries to see trend chart.</p>
            </div>
          ) : (
            <div style={{ background: "var(--color-background-primary)", border: "0.5px solid var(--color-border-tertiary)", borderRadius: "var(--border-radius-lg)", padding: "1.25rem" }}>
              <p style={{ margin: "0 0 1rem", fontSize: 13, fontWeight: 500, color: "var(--color-text-primary)" }}>BMI over time — {currentUser}</p>
              <div style={{ position: "relative", width: "100%", height: 260 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData} margin={{ top: 8, right: 16, bottom: 8, left: 0 }}>
                    <CartesianGrid stroke="rgba(128,128,128,0.12)" strokeDasharray="3 3" />
                    <XAxis dataKey="date" tick={{ fontSize: 11 }} />
                    <YAxis domain={['auto', 'auto']} tick={{ fontSize: 11 }} />
                    <Tooltip formatter={(v) => [v.toFixed(1), "BMI"]} contentStyle={{ fontSize: 12, borderRadius: 8 }} />
                    <ReferenceLine y={18.5} stroke="#378ADD" strokeDasharray="4 2" label={{ value: "18.5", position: "right", fontSize: 10, fill: "#378ADD" }} />
                    <ReferenceLine y={25} stroke="#639922" strokeDasharray="4 2" label={{ value: "25", position: "right", fontSize: 10, fill: "#639922" }} />
                    <ReferenceLine y={30} stroke="#BA7517" strokeDasharray="4 2" label={{ value: "30", position: "right", fontSize: 10, fill: "#BA7517" }} />
                    <Line type="monotone" dataKey="bmi" stroke="#639922" strokeWidth={2} dot={{ r: 4, fill: "#639922", strokeWidth: 0 }} activeDot={{ r: 6 }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
              <div style={{ display: "flex", gap: 16, marginTop: "0.75rem", flexWrap: "wrap" }}>
                {[{ c: "#378ADD", l: "Underweight < 18.5" }, { c: "#639922", l: "Normal 18.5–25" }, { c: "#BA7517", l: "Overweight 25–30" }, { c: "#E24B4A", l: "Obese > 30" }].map(b => (
                  <span key={b.l} style={{ display: "flex", alignItems: "center", gap: 5, fontSize: 11, color: "var(--color-text-secondary)" }}>
                    <span style={{ width: 10, height: 10, borderRadius: 2, background: b.c, flexShrink: 0 }} />{b.l}
                  </span>
                ))}
              </div>
            </div>
          )}

          {userRecords.length >= 2 && (
            <div style={{ marginTop: "1rem", background: "var(--color-background-primary)", border: "0.5px solid var(--color-border-tertiary)", borderRadius: "var(--border-radius-lg)", padding: "1.25rem" }}>
              <p style={{ margin: "0 0 0.75rem", fontSize: 13, fontWeight: 500 }}>Analysis</p>
              {[
                { label: "Average BMI", value: avgBMI },
                { label: "Total entries", value: userRecords.length },
                { label: "Overall change", value: trend !== null ? (parseFloat(trend) > 0 ? `+${trend}` : trend) : "–" },
                { label: "Latest status", value: userRecords[0] ? getBMIZone(userRecords[0].bmi).label : "–" },
              ].map(s => (
                <div key={s.label} style={{ display: "flex", justifyContent: "space-between", padding: "7px 0", borderBottom: "0.5px solid var(--color-border-tertiary)", fontSize: 13 }}>
                  <span style={{ color: "var(--color-text-secondary)" }}>{s.label}</span>
                  <span style={{ fontWeight: 500 }}>{s.value}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
