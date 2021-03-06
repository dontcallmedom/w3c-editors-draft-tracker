<xsl:stylesheet version="2.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:html="http://www.w3.org/1999/xhtml" exclude-result-prefixes="html svg xs" xmlns:svg="http://www.w3.org/2000/svg" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xlink="http://www.w3.org/1999/xlink">

<!-- Output method XML -->
<xsl:output method="xml" indent="yes"/>
<xsl:param name="end-month" select="current-date()"/>
<xsl:param name="start-month" select="$end-month - xs:yearMonthDuration('P0Y11M')"/>
<xsl:variable name="months" select="for $i in 0 to months-from-duration((($end-month - $start-month) div xs:dayTimeDuration('P1D')) idiv 30
   * xs:yearMonthDuration('P0Y1M') ) return ($start-month + $i * xs:yearMonthDuration('P0Y1M'))"/>
<xsl:param name="spec-title"/>

<xsl:variable name="monthNames" select="('January','February','March','April','May','June','July','August','September','October','November','December')"/>

<xsl:template match="/">
  <xsl:variable name="commits" select="log"/>
  <xsl:variable name="total" select="sum(for $i in $months return count($commits//logentry[starts-with(date, substring(xs:string($i),1,7))]))"/>
  <xsl:variable name="max" select="max(for $i in $months return count($commits//logentry[starts-with(date, substring(xs:string($i),1,7))]))"/>
  <xsl:variable name="height" select="max(($max,20)) + 20"/>
  <xsl:variable name="lastYearMonths" select="count(for $i in $months return if (year-from-date($i) &lt; year-from-date($end-month)) then $i else nil)"/>
  <svg xmlns="http://www.w3.org/2000/svg" width="{10*count($months)}" height="{$height + 54}">
    <style type="text/css">text { font-size:10px; text-anchor:middle;}
    line { stroke: #AAF; stroke-width:5px; }
    text.past { fill:#FFF;}
    a:link { fill: #00F; text-decoration: underline;}
    a:visited { fill: #F0F; text-decoration: underline;}
    </style>
    <title>Editing activity for <xsl:value-of select="$spec-title"/></title>
    <xsl:variable name="lastupdatemonth" select="number(substring(xs:string(/log/logentry[1]/date),6,2))"/>
    <desc title="{$total} commits since {$start-month}">Last updated <xsl:value-of select="$monthNames[$lastupdatemonth]"/><xsl:text> </xsl:text><xsl:value-of select="substring(/log/logentry[1]/date/text(),1,4)"/></desc>
    <rect x="0" y="{$height - 9}" width="{10*$lastYearMonths + 1}" height="25" fill="#999"/>
    <xsl:for-each select="$months">
      <xsl:variable name="month" select="$monthNames[month-from-date(current())]"/>
      <xsl:variable name="count" select="count($commits//logentry[starts-with(date, substring(xs:string(current()),1,7))])"/>
      <text x="{(position()-1)*10 + 5}" y="{$height}">
	<xsl:if test="year-from-date(current()) &lt; year-from-date($end-month)">
	  <xsl:attribute name="class">past</xsl:attribute>
	</xsl:if>
      <title><xsl:value-of select="$month"/><xsl:text> </xsl:text><xsl:value-of select="year-from-date(.)"/></title><xsl:value-of select="substring($month,1,1)"/></text>
      <line x1="{(position()-1)*10 + 5}" y1="{$height - 10}" x2="{(position()-1)*10 + 5}" y2="{$height - 10 - $count}">
	<title><xsl:value-of select="$count"/> commits in <xsl:value-of select="$month"/><xsl:text> </xsl:text><xsl:value-of select="year-from-date(.)"/></title>
      </line>
    </xsl:for-each>
    <text x="{5*$lastYearMonths}" y="{$height + 12}" class="past"><xsl:value-of select="year-from-date($end-month) - 1"/></text>
    <text x="{10*$lastYearMonths + 5*(12 - $lastYearMonths)}" y="{$height + 12}"><xsl:value-of select="year-from-date($end-month)"/></text>
    <text x="{10*count($months) div 2}" y="{$height + 24}">Commits on ed. draft</text>
    <xsl:if test="/log/issues">
      <text
          x="6.9628906"
          y="{$height + 36}"
          style="text-anchor:start"><a xlink:target="_parent" xlink:href="{/log/issues/open/@href}">Open Issues</a></text>
      <text
          x="6.9628906"
          y="{$height + 48}"
          style="text-anchor:start"><a xlink:target="_parent" xlink:href="{/log/pullrequests/@href}">Pull requests</a></text>
      <text
          x="112.83087"
          y="{$height + 36}"
          style="text-anchor:end"><a xlink:target="_parent" xlink:href="{/log/issues/open/@href}"><xsl:value-of select="/log/issues/open"/></a>/<xsl:value-of select="/log/issues/all"/></text>
      <text
          x="112.23766"
          y="{$height + 48}"
          style="text-anchor:end"><a xlink:target="_parent" xlink:href="{/log/pullrequests/@href}"><xsl:value-of select="/log/pullrequests"/></a></text>
    </xsl:if>
  </svg>
</xsl:template>

</xsl:stylesheet>
