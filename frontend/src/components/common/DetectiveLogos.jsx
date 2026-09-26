import React from 'react'

/**
 * High-fidelity SVG insignia and emblems for VERITAS
 * Authentic detective, criminal intelligence, forensic, and judicial seals.
 */

// 1. Official Detective Shield Badge (Law Enforcement / Criminal Intelligence)
export function DetectiveBadge({ className = "w-10 h-10", fill = "currentColor" }) {
  return (
    <svg
      viewBox="0 0 100 120"
      className={className}
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-label="Detective Shield Badge"
    >
      <defs>
        <linearGradient id="shieldGrad" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#9B93FF" stopOpacity="0.9" />
          <stop offset="50%" stopColor="#635BFF" stopOpacity="0.8" />
          <stop offset="100%" stopColor="#4A3EE0" stopOpacity="0.95" />
        </linearGradient>
        <linearGradient id="goldRibbon" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stopColor="#F5B041" />
          <stop offset="100%" stopColor="#D48207" />
        </linearGradient>
      </defs>

      {/* Outer Shield Boundary */}
      <path
        d="M50 4 L88 18 C88 58 74 94 50 114 C26 94 12 58 12 18 Z"
        fill="url(#shieldGrad)"
        stroke="#E3E4DF"
        strokeWidth="2.5"
        strokeLinejoin="round"
      />

      {/* Inner Inset Shield */}
      <path
        d="M50 11 L81 23 C81 56 69 88 50 105 C31 88 19 56 19 23 Z"
        fill="#171D2B"
        fillOpacity="0.4"
        stroke="#9B93FF"
        strokeWidth="1.2"
        strokeDasharray="2 2"
      />

      {/* Eagle Crest / Header Crown */}
      <path
        d="M40 18 Q50 12 60 18 L55 24 L50 21 L45 24 Z"
        fill="#FFFFFF"
        opacity="0.9"
      />

      {/* Five-Point Star Emblem */}
      <polygon
        points="50,28 54,40 66,40 56,48 60,60 50,52 40,60 44,48 34,40 46,40"
        fill="url(#goldRibbon)"
        stroke="#FFFFFF"
        strokeWidth="0.8"
      />

      {/* Forensic Reticle Center */}
      <circle cx="50" cy="46" r="4.5" fill="#171D2B" stroke="#72DBEF" strokeWidth="1" />
      <circle cx="50" cy="46" r="1.5" fill="#72DBEF" />

      {/* Central Banner Ribbon */}
      <path
        d="M24 68 L76 68 L70 79 L30 79 Z"
        fill="#101522"
        stroke="#E3E4DF"
        strokeWidth="1"
      />
      <text
        x="50"
        y="76"
        textAnchor="middle"
        fontSize="6"
        fontWeight="bold"
        fill="#FFFFFF"
        fontFamily="JetBrains Mono, monospace"
        letterSpacing="0.8"
      >
        CRIMINAL INTEL
      </text>

      {/* Bottom Laurel Branches */}
      <path
        d="M34 86 Q50 96 66 86"
        stroke="#79D8AD"
        strokeWidth="1.5"
        fill="none"
        strokeLinecap="round"
      />
      <circle cx="42" cy="91" r="1" fill="#79D8AD" />
      <circle cx="50" cy="93" r="1.2" fill="#79D8AD" />
      <circle cx="58" cy="91" r="1" fill="#79D8AD" />
    </svg>
  )
}

// 2. Crime Intelligence Bureau Official Circular Seal
export function CrimeIntelligenceSeal({ className = "w-10 h-10" }) {
  return (
    <svg
      viewBox="0 0 100 100"
      className={className}
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-label="Crime Intelligence Seal"
    >
      <circle cx="50" cy="50" r="46" stroke="#635BFF" strokeWidth="2.5" fill="#171D2B" fillOpacity="0.2" />
      <circle cx="50" cy="50" r="41" stroke="#E3E4DF" strokeWidth="1" strokeDasharray="3 3" />
      <circle cx="50" cy="50" r="32" stroke="#72DBEF" strokeWidth="1.5" fill="#101522" fillOpacity="0.4" />

      {/* Radar Coordinate Crosshairs */}
      <line x1="50" y1="12" x2="50" y2="88" stroke="#9B93FF" strokeWidth="0.8" strokeOpacity="0.5" />
      <line x1="12" y1="50" x2="88" y2="50" stroke="#9B93FF" strokeWidth="0.8" strokeOpacity="0.5" />

      {/* Central Network Nodes */}
      <circle cx="50" cy="50" r="5" fill="#635BFF" stroke="#FFFFFF" strokeWidth="1" />
      <circle cx="40" cy="38" r="3" fill="#72DBEF" />
      <circle cx="62" cy="42" r="3.5" fill="#FF9A7B" />
      <circle cx="46" cy="62" r="3" fill="#79D8AD" />
      <circle cx="60" cy="58" r="2.5" fill="#F5B041" />

      {/* Connecting Vector Lines */}
      <line x1="50" y1="50" x2="40" y2="38" stroke="#72DBEF" strokeWidth="1" />
      <line x1="50" y1="50" x2="62" y2="42" stroke="#FF9A7B" strokeWidth="1" />
      <line x1="50" y1="50" x2="46" y2="62" stroke="#79D8AD" strokeWidth="1" />
      <line x1="46" y1="62" x2="60" y2="58" stroke="#F5B041" strokeWidth="1" />

      {/* Decorative Outer Stars */}
      <circle cx="20" cy="32" r="1.5" fill="#F5B041" />
      <circle cx="80" cy="32" r="1.5" fill="#F5B041" />
      <circle cx="50" cy="94" r="1.5" fill="#F5B041" />
    </svg>
  )
}

// 3. Financial Crimes & Hawala Enforcement Division Emblem
export function FinancialCrimesBadge({ className = "w-10 h-10" }) {
  return (
    <svg
      viewBox="0 0 100 100"
      className={className}
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-label="Financial Crimes & Hawala Enforcement Badge"
    >
      <rect x="14" y="14" width="72" height="72" rx="14" fill="#171D2B" fillOpacity="0.3" stroke="#F5B041" strokeWidth="2" />
      <rect x="22" y="22" width="56" height="56" rx="8" fill="#101522" fillOpacity="0.5" stroke="#E3E4DF" strokeWidth="1" />

      {/* Bank Vault / Escrow Dial */}
      <circle cx="50" cy="50" r="18" stroke="#F5B041" strokeWidth="2.5" strokeDasharray="6 3" />
      <circle cx="50" cy="50" r="11" fill="#F5B041" fillOpacity="0.2" stroke="#FFFFFF" strokeWidth="1.2" />

      {/* Dial Spokes */}
      <line x1="50" y1="36" x2="50" y2="42" stroke="#FFFFFF" strokeWidth="1.5" />
      <line x1="50" y1="58" x2="50" y2="64" stroke="#FFFFFF" strokeWidth="1.5" />
      <line x1="36" y1="50" x2="42" y2="50" stroke="#FFFFFF" strokeWidth="1.5" />
      <line x1="58" y1="50" x2="64" y2="50" stroke="#FFFFFF" strokeWidth="1.5" />

      {/* Currency / Hawala Hash Node */}
      <circle cx="50" cy="50" r="3.5" fill="#FF9A7B" />

      {/* Flow Arrows */}
      <path d="M28 28 L38 28 M38 28 L34 24 M38 28 L34 32" stroke="#72DBEF" strokeWidth="1.5" strokeLinecap="round" />
      <path d="M72 72 L62 72 M62 72 L66 68 M62 72 L66 76" stroke="#72DBEF" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  )
}

// 4. Telecom CDR & Cyber Intercept Forensics Logo
export function TelecomForensicsLogo({ className = "w-10 h-10" }) {
  return (
    <svg
      viewBox="0 0 100 100"
      className={className}
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-label="Telecom Forensics Intercept Logo"
    >
      <circle cx="50" cy="50" r="44" fill="#171D2B" fillOpacity="0.3" stroke="#72DBEF" strokeWidth="2" />

      {/* Radio Wave Radii */}
      <path d="M30 40 Q50 20 70 40" stroke="#72DBEF" strokeWidth="1.5" fill="none" strokeOpacity="0.6" strokeDasharray="3 2" />
      <path d="M22 34 Q50 10 78 34" stroke="#72DBEF" strokeWidth="1.5" fill="none" strokeOpacity="0.4" />
      <path d="M38 46 Q50 32 62 46" stroke="#72DBEF" strokeWidth="1.8" fill="none" strokeOpacity="0.9" />

      {/* Central Radio Tower / Mast */}
      <path d="M50 48 L42 82 L58 82 Z" fill="#101522" stroke="#9B93FF" strokeWidth="1.5" />
      <line x1="44" y1="62" x2="56" y2="62" stroke="#E3E4DF" strokeWidth="1.2" />
      <line x1="43" y1="72" x2="57" y2="72" stroke="#E3E4DF" strokeWidth="1.2" />
      <line x1="46" y1="62" x2="54" y2="72" stroke="#9B93FF" strokeWidth="0.8" />
      <line x1="54" y1="62" x2="46" y2="72" stroke="#9B93FF" strokeWidth="0.8" />

      {/* Top Transmitter Pulse */}
      <circle cx="50" cy="46" r="4" fill="#FF9A7B" stroke="#FFFFFF" strokeWidth="1" />
      <circle cx="50" cy="46" r="7" stroke="#FF9A7B" strokeWidth="0.8" strokeOpacity="0.5" />
    </svg>
  )
}

// 5. Official Evidentiary Chain-of-Custody Stamp
export function EvidenceVaultSeal({ className = "w-12 h-12" }) {
  return (
    <svg
      viewBox="0 0 100 100"
      className={className}
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-label="Evidence Chain of Custody Seal"
    >
      <polygon
        points="50,5 64,15 80,10 88,25 100,36 98,52 100,68 88,78 80,93 64,88 50,97 36,88 20,93 12,78 0,68 2,52 0,36 12,25 20,10 36,15"
        fill="#171D2B"
        stroke="#79D8AD"
        strokeWidth="1.8"
      />
      <circle cx="50" cy="51" r="34" stroke="#79D8AD" strokeWidth="1.2" strokeDasharray="3 2" />

      {/* Padlock of Custody */}
      <rect x="38" y="47" width="24" height="20" rx="3" fill="#79D8AD" />
      <path
        d="M43 47 V39 C43 35 46 32 50 32 C54 32 57 35 57 39 V47"
        stroke="#FFFFFF"
        strokeWidth="2.5"
        fill="none"
        strokeLinecap="round"
      />
      <circle cx="50" cy="57" r="2.5" fill="#171D2B" />
      <line x1="50" y1="59.5" x2="50" y2="63" stroke="#171D2B" strokeWidth="1.5" />

      {/* Verified Text Stamp */}
      <text
        x="50"
        y="75"
        textAnchor="middle"
        fontSize="5"
        fontWeight="bold"
        fill="#FFFFFF"
        fontFamily="JetBrains Mono, monospace"
        letterSpacing="0.8"
      >
        ADMISSIBLE
      </text>
    </svg>
  )
}

// 6. Biometric Fingerprint Identifier
export function FingerprintIcon({ className = "w-6 h-6" }) {
  return (
    <svg
      viewBox="0 0 24 24"
      className={className}
      fill="none"
      stroke="currentColor"
      strokeWidth="1.5"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <path d="M12 2a10 10 0 0 0-10 10c0 4.2 2.6 7.8 6.4 9.3" />
      <path d="M14.5 4.5a7 7 0 0 0-8 6.5c0 3.3 1.8 6.1 4.5 7.5" />
      <path d="M12 8a4 4 0 0 0-4 4c0 2.2 1.2 4.1 3 5" />
      <path d="M12 12v3" />
      <path d="M16 11c0 3.5-1.5 6.5-4 8" />
      <path d="M19 8c.6 1.2 1 2.5 1 4 0 4-2.5 7.5-6 9" />
    </svg>
  )
}
