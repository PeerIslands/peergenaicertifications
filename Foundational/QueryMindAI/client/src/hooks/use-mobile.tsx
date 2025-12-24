import * as React from "react"

const MOBILE_BREAKPOINT = 768

/**
 * React hook that detects if the current viewport is mobile-sized.
 * Uses a media query to track window width and updates when the viewport size changes.
 * 
 * @returns A boolean indicating if the viewport width is below the mobile breakpoint (768px)
 * 
 * @remarks
 * The hook uses window.matchMedia to listen for viewport changes.
 * Returns undefined initially until the first measurement is complete.
 */
export function useIsMobile() {
  const [isMobile, setIsMobile] = React.useState<boolean | undefined>(undefined)

  React.useEffect(() => {
    const mql = window.matchMedia(`(max-width: ${MOBILE_BREAKPOINT - 1}px)`)
    const onChange = () => {
      setIsMobile(window.innerWidth < MOBILE_BREAKPOINT)
    }
    mql.addEventListener("change", onChange)
    setIsMobile(window.innerWidth < MOBILE_BREAKPOINT)
    return () => mql.removeEventListener("change", onChange)
  }, [])

  return !!isMobile
}
