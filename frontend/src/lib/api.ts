import axios from 'axios'
import { supabase } from './supabaseClient'

const apiUrl = import.meta.env.VITE_API_URL as string

export const api = axios.create({
  baseURL: apiUrl,
})

api.interceptors.request.use(async (config) => {
  const { data } = await supabase.auth.getSession()
  const token = data.session?.access_token
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})
