"use client";

import { useState, useEffect, useCallback } from "react";
import styles from "./page.module.css";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "https://pravah-s-2.onrender.com";

/* ─── Helpers ─── */
function formatPrice(num) {
  if (!num) return "₹0";
  if (num >= 10000000) return `₹${(num / 10000000).toFixed(2)} Cr`;
  if (num >= 100000) return `₹${(num / 100000).toFixed(2)} L`;
  return `₹${num.toLocaleString("en-IN")}`;
}

function formatPricePerSqft(num) {
  if (!num) return "₹0/sqft";
  return `₹${Math.round(num).toLocaleString("en-IN")}/sqft`;
}

function confidenceLabel(score) {
  if (score >= 0.85) return { text: "High", class: "success" };
  if (score >= 0.7) return { text: "Medium", class: "warning" };
  return { text: "Low", class: "info" };
}

/* ─── Icons (inline SVG) ─── */
function IconHome() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
      <polyline points="9 22 9 12 15 12 15 22" />
    </svg>
  );
}

function IconMapPin() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z" />
      <circle cx="12" cy="10" r="3" />
    </svg>
  );
}

function IconTrendingUp() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="23 6 13.5 15.5 8.5 10.5 1 18" />
      <polyline points="17 6 23 6 23 12" />
    </svg>
  );
}

function IconTarget() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10" /><circle cx="12" cy="12" r="6" /><circle cx="12" cy="12" r="2" />
    </svg>
  );
}

function IconBarChart() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="12" y1="20" x2="12" y2="10" /><line x1="18" y1="20" x2="18" y2="4" /><line x1="6" y1="20" x2="6" y2="16" />
    </svg>
  );
}

function IconSquare() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="3" y="3" width="18" height="18" rx="2" ry="2" />
    </svg>
  );
}

function IconCheck() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
      <polyline points="20 6 9 17 4 12" />
    </svg>
  );
}

function IconInfo() {
  return (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="10" /><line x1="12" y1="16" x2="12" y2="12" /><line x1="12" y1="8" x2="12.01" y2="8" />
    </svg>
  );
}

function IconArrowRight() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <line x1="5" y1="12" x2="19" y2="12" /><polyline points="12 5 19 12 12 19" />
    </svg>
  );
}

function IconBuilding() {
  return (
    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="4" y="2" width="16" height="20" rx="2" ry="2" /><path d="M9 22V12h6v10" /><path d="M8 6h.01M16 6h.01M12 6h.01M8 10h.01M16 10h.01M12 10h.01" />
    </svg>
  );
}


export default function Home() {
  const [locations, setLocations] = useState([]);
  const [formData, setFormData] = useState({
    location: "",
    area_sqft: "",
    bhk: "2",
    bathrooms: "2",
    floor: "",
    total_floors: "",
    age_of_property: "",
    parking: true,
    lift: true,
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [apiStatus, setApiStatus] = useState("checking");

  /* Fetch locations on mount */
  useEffect(() => {
    async function fetchLocations() {
      try {
        const res = await fetch(`${API_BASE}/api/v1/locations`);
        if (!res.ok) throw new Error("API unavailable");
        const data = await res.json();
        setLocations(data.locations || []);
        setApiStatus("connected");
        if (data.locations?.length > 0) {
          setFormData((prev) => ({ ...prev, location: data.locations[0].name }));
        }
      } catch {
        setApiStatus("error");
      }
    }
    fetchLocations();
  }, []);

  const handleChange = useCallback((e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({ ...prev, [name]: value }));
  }, []);

  const handleToggle = useCallback((field) => {
    setFormData((prev) => ({ ...prev, [field]: !prev[field] }));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const payload = {
        location: formData.location,
        area_sqft: parseFloat(formData.area_sqft),
        bhk: parseInt(formData.bhk, 10),
        bathrooms: parseInt(formData.bathrooms, 10),
        floor: parseInt(formData.floor, 10),
        total_floors: parseInt(formData.total_floors, 10),
        age_of_property: parseFloat(formData.age_of_property),
        parking: formData.parking,
        lift: formData.lift,
      };

      const res = await fetch(`${API_BASE}/api/v1/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || "Prediction failed");
      }

      const data = await res.json();
      setResult(data);
    } catch (err) {
      setError(err.message || "Something went wrong");
    } finally {
      setLoading(false);
    }
  };

  const selectedLocationStats = locations.find(
    (l) => l.name === formData.location
  );

  return (
    <div className={styles.page}>
      {/* ── Header ── */}
      <header className={styles.header}>
        <div className={`container ${styles.headerInner}`}>
          <div className={styles.logo}>
            <div className={styles.logoIcon}>
              <IconHome />
            </div>
            <div>
              <h1 className={styles.logoTitle}>NaviPrice</h1>
              <p className={styles.logoSubtitle}>AI-Powered Valuation</p>
            </div>
          </div>
          <div className={styles.headerRight}>
            <span
              className={`badge ${apiStatus === "connected"
                ? "badge-success"
                : apiStatus === "error"
                  ? "badge-warning"
                  : "badge-info"
                }`}
            >
              <span
                className={styles.statusDot}
                data-status={apiStatus}
              />
              {apiStatus === "connected"
                ? "API Connected"
                : apiStatus === "error"
                  ? "API Offline"
                  : "Checking..."}
            </span>
          </div>
        </div>
      </header>

      {/* ── Hero Section ── */}
      <section className={styles.hero}>
        <div className="container">
          <div className={styles.heroContent}>
            <div className={styles.heroBadge}>
              <IconTarget />
              <span>Powered by Gradient Boosting ML</span>
            </div>
            <h2 className={styles.heroTitle}>
              Predict House Prices in
              <span className={styles.heroGradient}> Navi Mumbai</span>
            </h2>
            <p className={styles.heroDescription}>
              Get instant, AI-powered property valuations across 9+ localities.
              Backed by data from 2,200+ real transactions with R² accuracy of 0.85.
            </p>
            <div className={styles.heroStats}>
              <div className={styles.heroStat}>
                <span className={styles.heroStatValue}>9+</span>
                <span className={styles.heroStatLabel}>Locations</span>
              </div>
              <div className={styles.heroDivider} />
              <div className={styles.heroStat}>
                <span className={styles.heroStatValue}>2,200+</span>
                <span className={styles.heroStatLabel}>Data Points</span>
              </div>
              <div className={styles.heroDivider} />
              <div className={styles.heroStat}>
                <span className={styles.heroStatValue}>0.85</span>
                <span className={styles.heroStatLabel}>R² Score</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ── Main Content ── */}
      <main className={`container ${styles.main}`}>
        <div className={styles.contentGrid}>
          {/* ── Form Panel ── */}
          <div className={styles.formPanel}>
            <div className={`glass-card ${styles.formCard}`}>
              <div className={styles.formHeader}>
                <IconBuilding />
                <div>
                  <h3 className={styles.formTitle}>Property Details</h3>
                  <p className={styles.formSubtitle}>
                    Enter property information to get a price estimate
                  </p>
                </div>
              </div>

              <form onSubmit={handleSubmit} className={styles.form} id="prediction-form">
                {/* Location */}
                <div className="input-group">
                  <label className="input-label" htmlFor="location">
                    <IconMapPin /> Location
                  </label>
                  <select
                    id="location"
                    name="location"
                    className="input-field"
                    value={formData.location}
                    onChange={handleChange}
                    required
                  >
                    {locations.map((loc) => (
                      <option key={loc.name} value={loc.name}>
                        {loc.name} ({formatPricePerSqft(loc.avg_price_per_sqft)})
                      </option>
                    ))}
                  </select>
                </div>

                {/* Area */}
                <div className="input-group">
                  <label className="input-label" htmlFor="area_sqft">
                    <IconSquare /> Carpet Area (sq.ft)
                  </label>
                  <input
                    id="area_sqft"
                    name="area_sqft"
                    type="number"
                    className="input-field"
                    placeholder="e.g. 1000"
                    value={formData.area_sqft}
                    onChange={handleChange}
                    min="100"
                    max="10000"
                    step="1"
                    required
                  />
                </div>

                {/* BHK & Bathrooms */}
                <div className={styles.formRow}>
                  <div className="input-group">
                    <label className="input-label" htmlFor="bhk">BHK</label>
                    <select
                      id="bhk"
                      name="bhk"
                      className="input-field"
                      value={formData.bhk}
                      onChange={handleChange}
                      required
                    >
                      {[1, 2, 3, 4, 5, 6].map((n) => (
                        <option key={n} value={n}>{n} BHK</option>
                      ))}
                    </select>
                  </div>
                  <div className="input-group">
                    <label className="input-label" htmlFor="bathrooms">Bathrooms</label>
                    <select
                      id="bathrooms"
                      name="bathrooms"
                      className="input-field"
                      value={formData.bathrooms}
                      onChange={handleChange}
                      required
                    >
                      {[1, 2, 3, 4, 5, 6].map((n) => (
                        <option key={n} value={n}>{n}</option>
                      ))}
                    </select>
                  </div>
                </div>

                {/* Floor & Total Floors */}
                <div className={styles.formRow}>
                  <div className="input-group">
                    <label className="input-label" htmlFor="floor">Floor</label>
                    <input
                      id="floor"
                      name="floor"
                      type="number"
                      className="input-field"
                      placeholder="e.g. 5"
                      value={formData.floor}
                      onChange={handleChange}
                      min="0"
                      max="100"
                      required
                    />
                  </div>
                  <div className="input-group">
                    <label className="input-label" htmlFor="total_floors">
                      Total Floors
                    </label>
                    <input
                      id="total_floors"
                      name="total_floors"
                      type="number"
                      className="input-field"
                      placeholder="e.g. 20"
                      value={formData.total_floors}
                      onChange={handleChange}
                      min="1"
                      max="80"
                      required
                    />
                  </div>
                </div>

                {/* Age of Property */}
                <div className="input-group">
                  <label className="input-label" htmlFor="age_of_property">
                    Property Age (years)
                  </label>
                  <input
                    id="age_of_property"
                    name="age_of_property"
                    type="number"
                    className="input-field"
                    placeholder="e.g. 5"
                    value={formData.age_of_property}
                    onChange={handleChange}
                    min="0"
                    max="50"
                    step="0.1"
                    required
                  />
                </div>

                {/* Amenities */}
                <div className={styles.amenitiesRow}>
                  <div className="toggle-container">
                    <div
                      className={`toggle ${formData.parking ? "active" : ""}`}
                      onClick={() => handleToggle("parking")}
                      role="switch"
                      aria-checked={formData.parking}
                      tabIndex={0}
                      id="toggle-parking"
                    />
                    <label className="input-label">Parking</label>
                  </div>
                  <div className="toggle-container">
                    <div
                      className={`toggle ${formData.lift ? "active" : ""}`}
                      onClick={() => handleToggle("lift")}
                      role="switch"
                      aria-checked={formData.lift}
                      tabIndex={0}
                      id="toggle-lift"
                    />
                    <label className="input-label">Lift</label>
                  </div>
                </div>

                {/* Submit */}
                <button
                  type="submit"
                  className={`btn btn-primary ${styles.submitBtn}`}
                  disabled={loading || apiStatus !== "connected"}
                  id="predict-button"
                >
                  {loading ? (
                    <>
                      <span className="spinner" />
                      Predicting...
                    </>
                  ) : (
                    <>
                      <IconTrendingUp />
                      Get Price Estimate
                      <IconArrowRight />
                    </>
                  )}
                </button>

                {error && (
                  <div className={styles.errorMsg}>
                    <IconInfo />
                    {error}
                  </div>
                )}
              </form>
            </div>

            {/* Location Quick Stats */}
            {selectedLocationStats && (
              <div className={`glass-card ${styles.locationCard}`}>
                <h4 className={styles.locationCardTitle}>
                  <IconMapPin />
                  {selectedLocationStats.name} Market Overview
                </h4>
                <div className={styles.locationStats}>
                  <div className={styles.locationStatItem}>
                    <span className={styles.locationStatLabel}>Avg Price</span>
                    <span className={styles.locationStatValue}>
                      {formatPrice(selectedLocationStats.avg_price)}
                    </span>
                  </div>
                  <div className={styles.locationStatItem}>
                    <span className={styles.locationStatLabel}>Price/sqft</span>
                    <span className={styles.locationStatValue}>
                      {formatPricePerSqft(
                        selectedLocationStats.avg_price_per_sqft
                      )}
                    </span>
                  </div>
                  <div className={styles.locationStatItem}>
                    <span className={styles.locationStatLabel}>Data Points</span>
                    <span className={styles.locationStatValue}>
                      {selectedLocationStats.count}
                    </span>
                  </div>
                  <div className={styles.locationStatItem}>
                    <span className={styles.locationStatLabel}>Range</span>
                    <span className={styles.locationStatValue}>
                      {formatPrice(selectedLocationStats.min_price)} –{" "}
                      {formatPrice(selectedLocationStats.max_price)}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* ── Results Panel ── */}
          <div className={styles.resultPanel}>
            {!result && !loading && (
              <div className={styles.emptyState}>
                <div className={styles.emptyIcon}>
                  <IconBarChart />
                </div>
                <h3>Your Estimate Will Appear Here</h3>
                <p>
                  Fill in the property details and click "Get Price Estimate" to
                  see your AI-powered valuation.
                </p>
              </div>
            )}

            {loading && (
              <div className={styles.loadingState}>
                <div className={styles.loadingPulse}>
                  <div className="spinner" style={{ width: 40, height: 40 }} />
                </div>
                <h3>Analyzing Property...</h3>
                <p>Running ML model for the best estimate</p>
              </div>
            )}

            {result && (
              <div className={styles.resultContent}>
                {/* Price Card */}
                <div className={`glass-card ${styles.priceCard}`}>
                  <div className={styles.priceHeader}>
                    <span className={styles.priceLabel}>Estimated Price</span>
                    <span
                      className={`badge badge-${confidenceLabel(result.confidence_score).class
                        }`}
                    >
                      <IconCheck />
                      {confidenceLabel(result.confidence_score).text} Confidence
                    </span>
                  </div>
                  <div className={styles.priceValue}>
                    {formatPrice(result.predicted_price)}
                  </div>
                  <div className={styles.priceRange}>
                    <span className={styles.priceRangeLabel}>Range:</span>
                    <span>
                      {formatPrice(result.price_range.low)} –{" "}
                      {formatPrice(result.price_range.high)}
                    </span>
                  </div>
                  <div className={styles.pricePerSqft}>
                    {formatPricePerSqft(result.price_per_sqft)}
                  </div>
                </div>

                {/* Location Context */}
                <div className={`glass-card ${styles.contextCard}`}>
                  <h4 className={styles.contextTitle}>
                    <IconMapPin />
                    {result.location_context.name} Market Context
                  </h4>
                  <div className={styles.contextGrid}>
                    <div className={styles.contextItem}>
                      <span className={styles.contextLabel}>Avg. Price</span>
                      <span className={styles.contextValue}>
                        {formatPrice(result.location_context.avg_price)}
                      </span>
                    </div>
                    <div className={styles.contextItem}>
                      <span className={styles.contextLabel}>Median Price</span>
                      <span className={styles.contextValue}>
                        {formatPrice(result.location_context.median_price)}
                      </span>
                    </div>
                    <div className={styles.contextItem}>
                      <span className={styles.contextLabel}>Avg ₹/sqft</span>
                      <span className={styles.contextValue}>
                        {formatPricePerSqft(
                          result.location_context.avg_price_per_sqft
                        )}
                      </span>
                    </div>
                    <div className={styles.contextItem}>
                      <span className={styles.contextLabel}>Data Points</span>
                      <span className={styles.contextValue}>
                        {result.location_context.data_points}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Feature Importance */}
                <div className={`glass-card ${styles.featureCard}`}>
                  <h4 className={styles.featureTitle}>
                    <IconBarChart />
                    What Drives the Price
                  </h4>
                  <div className={styles.featureList}>
                    {Object.entries(result.feature_importance)
                      .sort(([, a], [, b]) => b - a)
                      .map(([name, importance]) => (
                        <div key={name} className={styles.featureItem}>
                          <div className={styles.featureInfo}>
                            <span className={styles.featureName}>
                              {name.replace(/_/g, " ")}
                            </span>
                            <span className={styles.featurePercent}>
                              {(importance * 100).toFixed(1)}%
                            </span>
                          </div>
                          <div className={styles.featureBar}>
                            <div
                              className={styles.featureBarFill}
                              style={{ width: `${importance * 100}%` }}
                            />
                          </div>
                        </div>
                      ))}
                  </div>
                </div>

                {/* Input Summary */}
                <div className={`glass-card ${styles.summaryCard}`}>
                  <h4 className={styles.summaryTitle}>
                    <IconInfo />
                    Property Summary
                  </h4>
                  <div className={styles.summaryGrid}>
                    {Object.entries(result.input_summary).map(([key, val]) => (
                      <div key={key} className={styles.summaryItem}>
                        <span className={styles.summaryLabel}>
                          {key.replace(/_/g, " ")}
                        </span>
                        <span className={styles.summaryValue}>
                          {typeof val === "boolean"
                            ? val
                              ? "Yes ✓"
                              : "No ✗"
                            : typeof val === "number"
                              ? key.includes("area")
                                ? `${val} sq.ft`
                                : val
                              : val}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* ── Location Cards Section ── */}
      {locations.length > 0 && (
        <section className={styles.locationsSection}>
          <div className="container">
            <div className={styles.sectionHeader}>
              <h2 className={styles.sectionTitle}>
                Explore Navi Mumbai Localities
              </h2>
              <p className={styles.sectionSubtitle}>
                Avg. price per sq.ft across different nodes
              </p>
            </div>
            <div className={styles.locationsGrid}>
              {locations
                .sort((a, b) => b.avg_price_per_sqft - a.avg_price_per_sqft)
                .map((loc, idx) => (
                  <div
                    key={loc.name}
                    className={`glass-card ${styles.locationNodeCard}`}
                    style={{ animationDelay: `${idx * 0.08}s` }}
                    onClick={() => {
                      setFormData((prev) => ({ ...prev, location: loc.name }));
                      document
                        .getElementById("prediction-form")
                        ?.scrollIntoView({ behavior: "smooth" });
                    }}
                  >
                    <div className={styles.nodeHeader}>
                      <span className={styles.nodeName}>{loc.name}</span>
                      <span className={styles.nodeRank}>#{idx + 1}</span>
                    </div>
                    <div className={styles.nodePrice}>
                      {formatPricePerSqft(loc.avg_price_per_sqft)}
                    </div>
                    <div className={styles.nodeStats}>
                      <span>{loc.count} properties</span>
                      <span>
                        {formatPrice(loc.min_price)} – {formatPrice(loc.max_price)}
                      </span>
                    </div>
                  </div>
                ))}
            </div>
          </div>
        </section>
      )}

      {/* ── Footer ── */}
      <footer className={styles.footer}>
        <div className="container">
          <div className={styles.footerContent}>
            <div className={styles.footerBrand}>
              <div className={styles.logoIcon}>
                <IconHome />
              </div>
              <span className={styles.footerTitle}>NaviPrice</span>
            </div>
            <p className={styles.footerDisclaimer}>
              Disclaimer: Estimates are AI-generated and not certified
              valuations. Consult a professional appraiser for official
              valuations.
            </p>
            <p className={styles.footerCopy}>
              © 2026 NaviPrice • Built with ML & ❤️ for Navi Mumbai
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}
