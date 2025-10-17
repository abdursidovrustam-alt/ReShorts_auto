/** @type {import('tailwindcss').Config} */
module.exports = {
	darkMode: ['class'],
	content: [
		'./pages/**/*.{ts,tsx}',
		'./components/**/*.{ts,tsx}',
		'./app/**/*.{ts,tsx}',
		'./src/**/*.{ts,tsx}',
	],
	theme: {
		container: {
			center: true,
			padding: '2rem',
			screens: {
				'2xl': '1400px',
			},
		},
		extend: {
			colors: {
				primary: {
					400: '#22D3EE',
					500: '#06B6D4',
					600: '#0891B2',
					700: '#0E7490',
					900: '#164E63',
					DEFAULT: '#06B6D4',
					foreground: '#0A0A0A',
				},
				neutral: {
					50: '#FAFAFA',
					100: '#F5F5F5',
					400: '#A3A3A3',
					500: '#737373',
					700: '#404040',
					800: '#262626',
					900: '#171717',
					950: '#0A0A0A',
				},
				background: {
					base: '#171717',
					surface: '#262626',
					elevated: '#404040',
					modal: '#404040',
					DEFAULT: '#171717',
				},
				foreground: '#F5F5F5',
				success: '#10B981',
				warning: '#F59E0B',
				error: '#EF4444',
				info: '#3B82F6',
				border: '#404040',
				input: '#404040',
				ring: '#06B6D4',
				secondary: {
					DEFAULT: '#262626',
					foreground: '#F5F5F5',
				},
				accent: {
					DEFAULT: '#404040',
					foreground: '#F5F5F5',
				},
				destructive: {
					DEFAULT: '#EF4444',
					foreground: '#FAFAFA',
				},
				muted: {
					DEFAULT: '#262626',
					foreground: '#A3A3A3',
				},
				popover: {
					DEFAULT: '#262626',
					foreground: '#F5F5F5',
				},
				card: {
					DEFAULT: '#262626',
					foreground: '#F5F5F5',
				},
			},
			spacing: {
				xs: '4px',
				sm: '8px',
				md: '16px',
				lg: '24px',
				xl: '32px',
				'2xl': '48px',
				'3xl': '64px',
				'4xl': '96px',
			},
			borderRadius: {
				sm: '4px',
				md: '8px',
				lg: '12px',
				xl: '16px',
			},
			boxShadow: {
				sm: '0 1px 2px rgba(0, 0, 0, 0.3)',
				md: '0 4px 6px rgba(0, 0, 0, 0.4)',
				lg: '0 10px 15px rgba(0, 0, 0, 0.5)',
				glow: '0 0 20px rgba(6, 182, 212, 0.3)',
				'glow-strong': '0 0 30px rgba(6, 182, 212, 0.5)',
			},
			transitionDuration: {
				fast: '150ms',
				normal: '250ms',
				smooth: '300ms',
				slow: '400ms',
			},
			keyframes: {
				'accordion-down': {
					from: { height: 0 },
					to: { height: 'var(--radix-accordion-content-height)' },
				},
				'accordion-up': {
					from: { height: 'var(--radix-accordion-content-height)' },
					to: { height: 0 },
				},
			},
			animation: {
				'accordion-down': 'accordion-down 0.2s ease-out',
				'accordion-up': 'accordion-up 0.2s ease-out',
			},
			fontFamily: {
				sans: ['Inter', 'system-ui', 'sans-serif'],
				mono: ['JetBrains Mono', 'monospace'],
			},
		},
	},
	plugins: [require('tailwindcss-animate')],
}
