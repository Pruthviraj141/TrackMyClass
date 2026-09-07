import { useState } from "react"
import { useQuery } from "@tanstack/react-query"
import { api, API_BASE_URL } from "@/lib/api"
import { FileText, Download } from "lucide-react"

import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Button } from "@/components/ui/button"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "@/components/ui/table"
import { Skeleton } from "@/components/ui/skeleton"

export default function Reports() {
  const [date, setDate] = useState(new Date().toISOString().split("T")[0])
  const [subject, setSubject] = useState("All")

  const { data, isLoading } = useQuery({
    queryKey: ["historicalData", date, subject],
    queryFn: async () => {
      const res = await api.get("/admin/historical-data", {
        params: {
          date: date ? format(new Date(date), "yyyy-MM-dd") : undefined,
          subject: subject === "All" ? undefined : subject
        }
      })
      return res.data
    },
  })

  const exportUrl = `${API_BASE_URL.replace("/api", "/admin")}/export-historical-csv?date=${date}&subject=${subject}&format=`

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold tracking-tight">Reports</h1>
          <p className="text-muted-foreground">View and export historical attendance records.</p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2"><FileText className="h-5 w-5" /> Filter Records</CardTitle>
          <CardDescription>Select a date and subject to view the attendance report.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
            <div className="space-y-2">
              <Label htmlFor="date">Date</Label>
              <Input 
                id="date" 
                type="date" 
                value={date}
                onChange={(e) => setDate(e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="subject">Subject</Label>
              <select 
                id="subject"
                value={subject}
                onChange={(e) => setSubject(e.target.value)}
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2"
              >
                <option value="All">All Subjects</option>
                {data?.available_subjects?.map((sub: string) => (
                  <option key={sub} value={sub}>{sub}</option>
                ))}
              </select>
            </div>
            <div className="space-y-2 flex flex-col justify-end">
              <div className="flex gap-2">
                <Button variant="outline" className="w-full" onClick={() => window.location.href = exportUrl + "csv"}>
                  <Download className="mr-2 h-4 w-4" /> CSV
                </Button>
                <Button variant="outline" className="w-full" onClick={() => window.location.href = exportUrl + "excel"}>
                  <Download className="mr-2 h-4 w-4" /> Excel
                </Button>
                <Button variant="outline" className="w-full" onClick={() => window.location.href = exportUrl + "pdf"}>
                  <Download className="mr-2 h-4 w-4" /> PDF
                </Button>
              </div>
            </div>
          </div>

          <div className="rounded-md border">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Student Name</TableHead>
                  <TableHead>Roll Number</TableHead>
                  <TableHead>Time</TableHead>
                  <TableHead>Confidence</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {isLoading ? (
                  Array.from({ length: 3 }).map((_, i) => (
                    <TableRow key={i}>
                      <TableCell><Skeleton className="h-4 w-24" /></TableCell>
                      <TableCell><Skeleton className="h-4 w-16" /></TableCell>
                      <TableCell><Skeleton className="h-4 w-16" /></TableCell>
                      <TableCell><Skeleton className="h-4 w-12" /></TableCell>
                    </TableRow>
                  ))
                ) : data?.present_list?.length > 0 ? (
                  data.present_list.map((record: any, idx: number) => (
                    <TableRow key={idx}>
                      <TableCell className="font-medium">{record.name}</TableCell>
                      <TableCell>{record.roll_number}</TableCell>
                      <TableCell>{record.time}</TableCell>
                      <TableCell>{(record.confidence * 100).toFixed(1)}%</TableCell>
                    </TableRow>
                  ))
                ) : (
                  <TableRow>
                    <TableCell colSpan={4} className="h-24 text-center text-muted-foreground">
                      No records found for this date.
                    </TableCell>
                  </TableRow>
                )}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
