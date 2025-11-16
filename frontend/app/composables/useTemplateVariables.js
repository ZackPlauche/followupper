/**
 * Composable for template variable replacement
 * Handles all template variable and conditional logic
 */
export const useTemplateVariables = () => {
  /**
   * Replace template variables in text
   * @param {string} text - The template text
   * @param {Object} options - Options for replacement
   * @param {Object} options.contact - Contact data (for real replacements)
   * @param {string} options.frequencyType - Frequency type (daily, weekly, etc.)
   * @param {string} options.frequency - Frequency display string
   * @param {number} options.frequencyDays - Frequency days
   * @param {boolean} options.useSampleData - Use sample data instead of contact data (for previews)
   * @returns {string} - Text with variables replaced
   */
  const replaceTemplateVariables = (text, options = {}) => {
    if (!text) return ''

    const {
      contact = null,
      frequencyType = null,
      frequency = '',
      frequencyDays = '',
      useSampleData = false
    } = options

    // Sample data for previews
    const sampleContact = {
      name: 'John Doe',
      first_name: 'John',
      preferred_name: 'Johnny',
      last_name: 'Doe',
      email: 'john@example.com',
      codementor_username: 'johndoe',
      gender: 'male'
    }

    // Use sample data or real contact data
    const contactData = useSampleData ? sampleContact : (contact || sampleContact)
    
    // Extract name parts
    const nameParts = (contactData.name || '').split(' ')
    const firstName = contactData.preferred_name || nameParts[0] || contactData.first_name || ''
    const lastName = nameParts.slice(1).join(' ') || contactData.last_name || ''
    const preferredName = contactData.preferred_name || firstName
    const gender = contactData.gender || ''

    let result = text

    // 1. Handle gender-based conditionals
    if (gender === 'male') {
      result = result.replace(/\{if_male:([^}]+)\}/g, '$1')
      result = result.replace(/\{if_female:([^}]+)\}/g, '')
    } else if (gender === 'female') {
      result = result.replace(/\{if_female:([^}]+)\}/g, '$1')
      result = result.replace(/\{if_male:([^}]+)\}/g, '')
    } else {
      result = result.replace(/\{if_male:([^}]+)\}/g, '')
      result = result.replace(/\{if_female:([^}]+)\}/g, '')
    }

    // 2. Handle frequency conditionals
    if (frequencyType) {
      const frequencyConditionals = {
        'daily': 'if_frequency_daily',
        'weekly': 'if_frequency_week',
        'monthly': 'if_frequency_month',
        'quarterly': 'if_frequency_quarter',
        'yearly': 'if_frequency_year',
        'custom': 'if_frequency_custom'
      }
      const currentConditional = frequencyConditionals[frequencyType]
      
      Object.values(frequencyConditionals).forEach(conditional => {
        const pattern = new RegExp(`\\{${conditional}:([^}]+)\\}`, 'g')
        if (conditional === currentConditional) {
          result = result.replace(pattern, '$1')
        } else {
          result = result.replace(pattern, '')
        }
      })
    } else {
      // Remove all frequency conditionals if no frequency context
      const frequencyConditionals = [
        'if_frequency_daily', 'if_frequency_week', 'if_frequency_month',
        'if_frequency_quarter', 'if_frequency_year', 'if_frequency_custom'
      ]
      frequencyConditionals.forEach(conditional => {
        result = result.replace(new RegExp(`\\{${conditional}:([^}]+)\\}`, 'g'), '')
      })
    }

    // 3. Determine current season and holiday
    const now = new Date()
    const month = now.getMonth() + 1
    const day = now.getDate()

    // Determine season
    let season = null
    if ((month === 3 && day >= 20) || [4, 5].includes(month) || (month === 6 && day < 21)) {
      season = 'spring'
    } else if ((month === 6 && day >= 21) || [7, 8].includes(month) || (month === 9 && day < 23)) {
      season = 'summer'
    } else if ((month === 9 && day >= 23) || [10, 11].includes(month) || (month === 12 && day < 21)) {
      season = 'fall'
    } else {
      season = 'winter'
    }

    // Determine holiday
    let holiday = null
    if (month === 12) holiday = 'christmas'
    else if (month === 10) holiday = 'halloween'
    else if (month === 11 && day >= 20) holiday = 'thanksgiving'
    else if ((month === 3 && day >= 20) || (month === 4 && day <= 30)) holiday = 'easter'
    else if (month === 1 && day <= 7) holiday = 'newyear'

    // 4. Handle seasonal conditionals
    const seasonConditionals = ['if_spring', 'if_summer', 'if_fall', 'if_winter']
    seasonConditionals.forEach(seasonConditional => {
      const seasonName = seasonConditional.replace('if_', '')
      const pattern = new RegExp(`\\{${seasonConditional}:([^}]+)\\}`, 'g')
      if (season === seasonName) {
        result = result.replace(pattern, '$1')
      } else {
        result = result.replace(pattern, '')
      }
    })

    // 5. Handle holiday conditionals (new naming: if_X, also support old if_season_X)
    const holidayConditionals = ['if_christmas', 'if_halloween', 'if_thanksgiving', 'if_easter', 'if_newyear']
    const oldHolidayConditionals = ['if_season_christmas', 'if_season_halloween', 'if_season_thanksgiving', 'if_season_easter', 'if_season_newyear']
    
    ;[...holidayConditionals, ...oldHolidayConditionals].forEach(holidayConditional => {
      const holidayName = holidayConditional.startsWith('if_season_') 
        ? holidayConditional.replace('if_season_', '')
        : holidayConditional.replace('if_', '')
      const escaped = holidayConditional.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
      const pattern = new RegExp(`\\{${escaped}:([^}]+)\\}`, 'g')
      if (holiday === holidayName) {
        result = result.replace(pattern, '$1')
      } else {
        result = result.replace(pattern, '')
      }
    })

    // 6. Process generic if_holiday conditional
    if (holiday) {
      result = result.replace(/\{if_holiday:([^}]+)\}/g, '$1')
    } else {
      result = result.replace(/\{if_holiday:([^}]+)\}/g, '')
    }

    // 7. Determine frequency word (day, week, month, quarter, year)
    let frequencyWord = ''
    if (frequencyType) {
      const frequencyMap = {
        'daily': 'day',
        'weekly': 'week',
        'monthly': 'month',
        'quarterly': 'quarter',
        'yearly': 'year',
        'custom': 'period'
      }
      frequencyWord = frequencyMap[frequencyType] || ''
    }

    // 8. Replace variables
    result = result.replace(/\{name\}/g, contactData.name || '')
    result = result.replace(/\{first_name\}/g, firstName)
    result = result.replace(/\{preferred_name\}/g, preferredName)
    result = result.replace(/\{last_name\}/g, lastName)
    result = result.replace(/\{gender\}/g, gender)
    result = result.replace(/\{email\}/g, contactData.email || '')
    result = result.replace(/\{codementor_username\}/g, contactData.codementor_username || '')
    result = result.replace(/\{frequency\}/g, frequencyWord)
    result = result.replace(/\{frequency_days\}/g, String(frequencyDays))
    result = result.replace(/\{season\}/g, season ? season.charAt(0).toUpperCase() + season.slice(1) : '')
    result = result.replace(/\{holiday\}/g, holiday ? holiday.charAt(0).toUpperCase() + holiday.slice(1) : '')

    // 9. Add date variables (last_month, last_year, day, month)
    const lastMonthDate = new Date(now.getFullYear(), now.getMonth() - 1, 1)
    const lastMonthName = lastMonthDate.toLocaleString('default', { month: 'long' })
    const currentMonthName = now.toLocaleString('default', { month: 'long' })
    const lastYear = String(now.getFullYear() - 1)
    const dayName = now.toLocaleString('default', { weekday: 'long' })
    result = result.replace(/\{last_month\}/g, lastMonthName)
    result = result.replace(/\{last_year\}/g, lastYear)
    result = result.replace(/\{day\}/g, dayName)
    result = result.replace(/\{month\}/g, currentMonthName)

    // 9. Replace old syntax for backwards compatibility
    result = result.replace(/\{contact\.name\}/g, contactData.name || '')
    result = result.replace(/\{contact\.first_name\}/g, firstName)
    result = result.replace(/\{contact\.preferred_name\}/g, preferredName)
    result = result.replace(/\{contact\.last_name\}/g, lastName)
    result = result.replace(/\{contact\.gender\}/g, gender)
    result = result.replace(/\{contact\.email\}/g, contactData.email || '')
    result = result.replace(/\{contact\.codementor_username\}/g, contactData.codementor_username || '')

    return result
  }

  return {
    replaceTemplateVariables
  }
}

