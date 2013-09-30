<xsl:stylesheet version="2.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:html="http://www.w3.org/1999/xhtml" exclude-result-prefixes="html" xmlns:svg="http://www.w3.org/2000/svg" xmlns:xs="http://www.w3.org/2001/XMLSchema"> 

<!-- Output method XML -->
<xsl:output method="xml" indent="yes"/>
<xsl:param name="start-month" select="current-date() - xs:yearMonthDuration('P0Y11M')"/>
<xsl:param name="end-month" select="current-date()"/>
<xsl:variable name="months" select="for $i in 0 to months-from-duration((($end-month - $start-month) div xs:dayTimeDuration('P1D')) idiv 30 
   * xs:yearMonthDuration('P0Y1M') ) return ($start-month + $i * xs:yearMonthDuration('P0Y1M'))"/>
<xsl:param name="spec-title"/>

<xsl:variable name="monthNames" select="('January','February','March','April','May','June','July','August','September','October','November','December')"/>

<xsl:param name="src" select="'gum-commits.xml'"/>
<xsl:variable name="commits" select="document($src)/entries"/>

<xsl:template match="/">
  <svg xmlns="http://www.w3.org/2000/svg" viewBox="-5 0 {10*count($months)} 100">
    <style type="text/css">text { font-size:10px; text-anchor:middle;}
    line { stroke: #AAF; stroke-width:5px; }
    </style>
    <title>Editing activity for <xsl:value-of select="$spec-title"/></title>
    <xsl:for-each select="$months">
      <xsl:variable name="month" select="$monthNames[month-from-date(current())]"/>
      <xsl:variable name="count" select="count($commits/entry[starts-with(commit_date, substring(xs:string(current()),1,7))])"/>
      <text x="{(position()-1)*10}" y="100"><title><xsl:value-of select="$month"/><xsl:text> </xsl:text><xsl:value-of select="year-from-date(.)"/></title><xsl:value-of select="substring($month,1,1)"/></text>
      <line x1="{(position()-1)*10}" y1="90" x2="{(position()-1)*10}" y2="{90 - $count}">
	<title><xsl:value-of select="$count"/> commits in <xsl:value-of select="$month"/><xsl:text> </xsl:text><xsl:value-of select="year-from-date(.)"/></title>
      </line>
    </xsl:for-each>
  </svg>
</xsl:template>

</xsl:stylesheet>