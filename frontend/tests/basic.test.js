import { describe, it, expect } from 'vitest'

describe('Basic Test Suite', () => {
  it('should pass a simple test', () => {
    expect(1 + 1).toBe(2)
  })

  it('should test string manipulation', () => {
    const str = 'Clarity'
    expect(str.toLowerCase()).toBe('clarity')
  })

  it('should test array operations', () => {
    const arr = [1, 2, 3]
    expect(arr).toHaveLength(3)
    expect(arr).toContain(2)
  })
})
