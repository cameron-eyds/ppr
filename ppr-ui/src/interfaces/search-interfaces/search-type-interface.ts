import type {
  APIMHRMapSearchTypes,
  APISearchTypes,
  BlankSearchTypes,
  UIMHRSearchTypes,
  UISearchTypes
} from '@/enums'
import type { HintIF } from '.'

// Search type interface
export interface SearchTypeIF {
  divider: boolean
  hints: HintIF
  selectDisabled: boolean
  searchTypeUI: UISearchTypes|UIMHRSearchTypes
  searchTypeAPI: APISearchTypes|APIMHRMapSearchTypes|BlankSearchTypes
  textLabel: string
  group: number
  class?: string
  icon?: string
  color?: string
}
