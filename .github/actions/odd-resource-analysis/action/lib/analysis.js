const { sampleCorrelation, tTest } = require('simple-statistics')
const { MINIMUM_VALID_SAMPLE_SIZE } = require('./constants')

const P_VALUE_THRESHOLD = 0.05

const CORRELATION_THRESHOLDS = {
  STRONG: 0.7,
  MODERATE: 0.3,
}

/**
 * @description Calculates one-tailed p-value for correlation coefficient
 * @param {number} correlation Pearson correlation coefficient
 * @param {number} sampleSize Number of samples
 * @returns {number} One-tailed p-value
 */
function calculatePValue(correlation, sampleSize) {
  const t = correlation * Math.sqrt((sampleSize - 2) / (1 - correlation ** 2))

  const twoTailedPValue = tTest([t], 0)

  // Convert to one-tailed p-value
  return twoTailedPValue / 2
}

/**
 * @description Determines correlation strength and direction
 * @param {number} correlation Pearson correlation coefficient
 * @returns {string} Human readable interpretation
 */
function getCorrelationDescription(correlation) {
  const strength = Math.abs(correlation)
  const direction = correlation > 0 ? 'positive' : 'negative'

  if (strength > CORRELATION_THRESHOLDS.STRONG) {
    return `Strong ${direction} correlation (>${CORRELATION_THRESHOLDS.STRONG})`
  } else if (strength > CORRELATION_THRESHOLDS.MODERATE) {
    return `Moderate ${direction} correlation (>${CORRELATION_THRESHOLDS.MODERATE} and <${CORRELATION_THRESHOLDS.STRONG})`
  }
  return `Weak ${direction} correlation (<=${CORRELATION_THRESHOLDS.MODERATE})`
}

/**
 * @description Performs complete correlation analysis including significance testing
 * @param {Array<number>} x Array of numbers
 * @param {Array<number>} y Array of numbers
 * @return {Object} Analysis results including correlation, significance, and interpretation
 */
function analyzeCorrelation(x, y) {
  const lowestSampleSize = Math.min(x.length, y.length)

  if (lowestSampleSize < MINIMUM_VALID_SAMPLE_SIZE) {
    return {
      correlation: 0,
      isSignificant: false,
      sampleSize: lowestSampleSize,
      pValue: 1,
      interpretation: 'Not enough samples for analysis',
    }
  }

  const correlation = sampleCorrelation(x, y)
  const pValue = calculatePValue(correlation, lowestSampleSize)
  const isSignificant = pValue < P_VALUE_THRESHOLD

  return {
    correlation,
    isSignificant,
    sampleSize: x.length,
    pValue,
    interpretation: isSignificant
      ? getCorrelationDescription(correlation)
      : 'No significant correlation found',
  }
}

module.exports = {
  analyzeCorrelation,
}
