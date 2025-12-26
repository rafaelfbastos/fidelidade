export interface CompanyMemberUser {
  id: number
  email: string
  first_name: string
  last_name: string
  full_name: string
  phone: string | null
}

export interface CompanyMemberRecord {
  uuid: string
  role: 'owner' | 'admin' | 'attendant'
  role_display: string
  is_active: boolean
  created_at: string
  user: CompanyMemberUser
}

export interface PaginatedResponse<T> {
  count: number
  next: string | null
  previous: string | null
  results: T[]
}
