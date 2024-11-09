import { NextApiRequest, NextApiResponse } from 'next'
import { NextResponse } from 'next/server'

type Departure = {
  time: string
  routeNumber: string
  routeColor: string
  routeTextColor: string
  headsign: string
  global_stop_id: string
  stop_code: string
  branch_code: string
}

